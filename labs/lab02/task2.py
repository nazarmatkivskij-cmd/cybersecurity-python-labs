import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# Налаштування логування
logging.basicConfig (
		level = logging.INFO ,
		format = "[%(levelname)s] %(asctime)s - %(message)s" ,
		datefmt = "%Y-%m-%d %H:%M:%S" ,
		)
logger = logging.getLogger ( __name__ )


@dataclass
class SudoExecution :
	timestamp: str
	user: str
	tty: str
	pwd: str
	target_user: str
	command: str


def parse_sudo_log ( log_file_path: Path ) -> list [ SudoExecution ] :
	"""Парсить лог файл sudo за допомогою регулярних виразів з обробкою винятків."""
	entries = [ ]
	pattern = re.compile (
			r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+sudo:\s+(?P<user>\S+)\s*:\s+TTY=(?P<tty>\S+)\s*;\s+PWD=(?P<pwd>\S+)\s*;\s+USER=(?P<target_user>\S+)\s*;\s+COMMAND=(?P<command>.+)$"
			)
	
	if not log_file_path.exists ( ) :
		logger.error ( f"Файл логу не знайдено: {log_file_path}" )
		return entries
	
	# Обробка винятків (Exceptions) при читанні файлу
	try :
		with open ( log_file_path , "r" , encoding = "utf-8" ) as f :
			for line in f :
				match = pattern.match ( line.strip ( ) )
				if match :
					data = match.groupdict ( )
					entries.append (
							SudoExecution (
									timestamp = data [ "timestamp" ] ,
									user = data [ "user" ] ,
									tty = data [ "tty" ] ,
									pwd = data [ "pwd" ] ,
									target_user = data [ "target_user" ] ,
									command = data [ "command" ] ,
									)
							)
	except PermissionError :
		logger.error ( f"Помилка доступу: недостатньо прав для читання файлу {log_file_path}" )
	except UnicodeDecodeError :
		logger.error ( f"Помилка кодування: неможливо прочитати файл {log_file_path} у форматі UTF-8" )
	except Exception as e :
		logger.error ( f"Непередбачена помилка під час читання файлу {log_file_path}: {e}" )
	
	return entries


def analyze_sudo_logs ( log_file: str , alert_commands_list: list [ str ] , output_json: str ) :
	path = Path ( log_file )
	logger.info ( f"Parsing sudo usage logs from {path}..." )
	
	executions = parse_sudo_log ( path )
	total_commands = len ( executions )
	logger.info ( f"Processed {total_commands:,} privileged execution entries." )
	
	root_executions = sum ( 1 for e in executions if e.target_user == "root" )
	
	print ( "\n=== Privileged Execution Summary ===" )
	print ( f"Total Sudo Commands: {total_commands:,}" )
	print ( f"Root Executions    : {root_executions:,}" )
	
	# Пошук підозрілих команд
	suspicious_keywords = [
			"chmod 777" ,
			"nc" ,
			"nmap" ,
			"dd" ,
			"/etc/shadow" ,
			"bash" ,
			"sh" ,
			]
	if alert_commands_list :
		suspicious_keywords.extend ( alert_commands_list )
	
	suspicious_findings = [ ]
	user_command_counts = Counter ( )
	user_high_risk_counts = Counter ( )
	
	for e in executions :
		user_command_counts [ e.user ] += 1
		is_suspicious = any ( kw in e.command for kw in suspicious_keywords )
		if is_suspicious :
			suspicious_findings.append ( e )
			user_high_risk_counts [ e.user ] += 1
	
	print ( "\n=== Suspicious / High-Risk Command Executions ===" )
	for e in suspicious_findings :
		msg = f"[ALERT] User '{e.user}' executed: 'sudo {e.command}' on TTY={e.tty}"
		print ( msg )
		logger.warning ( msg )
	
	print ( "\n=== Top Sudo Users ===" )
	top_users = user_command_counts.most_common ( 5 )
	for idx , (usr , count) in enumerate ( top_users , 1 ) :
		high_risk_count = user_high_risk_counts [ usr ]
		risk_info = (
				f" (High risk commands: {high_risk_count})" if high_risk_count > 0 else ""
		)
		print ( f"{idx}. {usr} : {count} commands{risk_info}" )
	
	# Збереження результатів у JSON з обробкою винятків
	output_path = Path ( output_json )
	
	report_data = {
			"total_commands" : total_commands ,
			"root_executions" : root_executions ,
			"suspicious_count" : len ( suspicious_findings ) ,
			"top_users" : top_users ,
			"suspicious_findings" : [
					{
							"timestamp" : e.timestamp ,
							"user" : e.user ,
							"tty" : e.tty ,
							"target_user" : e.target_user ,
							"command" : e.command ,
							}
					for e in suspicious_findings
					] ,
			}
	
	try :
		output_path.parent.mkdir ( parents = True , exist_ok = True )
		with open ( output_path , "w" , encoding = "utf-8" ) as f :
			json.dump ( report_data , f , indent = 4 , ensure_ascii = False )
		logger.info ( f"Privileged command audit saved to {output_path}" )
	except PermissionError :
		logger.error ( f"Помилка доступу: відсутні права на запис файлу за шляхом {output_path}" )
	except Exception as e :
		logger.error ( f"Не вдалося зберегти JSON-звіт у файл {output_path}: {e}" )