#!/usr/bin/env python3
"""
SSL/TLS Certificate Expiry Date Checker
This script checks SSL certificate expiration dates for websites defined in a config file
and provides alerting capabilities via email or webhook notifications.
"""

import ssl
import socket
import json
import yaml
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Tuple, Optional
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CertificateChecker:
    """Main class for checking SSL certificate expiration dates"""
    
    def __init__(self, config_path: str):
        """
        Initialize the certificate checker with configuration
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from YAML or JSON file
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary containing configuration
        """
        try:
            with open(config_path, 'r') as file:
                if config_path.endswith('.json'):
                    return json.load(file)
                elif config_path.endswith(('.yml', '.yaml')):
                    return yaml.safe_load(file)
                else:
                    raise ValueError("Config file must be JSON or YAML")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def get_certificate_expiry(self, hostname: str, port: int = 443, timeout: int = 10) -> Tuple[str, Optional[datetime], Optional[str]]:
        """
        Get SSL certificate expiration date for a given hostname
        
        Args:
            hostname: The hostname to check
            port: Port number (default 443)
            timeout: Connection timeout in seconds
            
        Returns:
            Tuple of (hostname, expiry_date, error_message)
        """
        try:
            logger.info(f"Checking certificate for {hostname}:{port}")
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and retrieve certificate
            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
                    cert = secure_sock.getpeercert()
                    
            # Parse expiration date
            expiry_date_str = cert['notAfter']
            expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
            
            return hostname, expiry_date, None
            
        except socket.timeout:
            error_msg = f"Connection timeout for {hostname}"
            logger.error(error_msg)
            return hostname, None, error_msg
        except socket.gaierror:
            error_msg = f"DNS resolution failed for {hostname}"
            logger.error(error_msg)
            return hostname, None, error_msg
        except ssl.SSLError as e:
            error_msg = f"SSL error for {hostname}: {str(e)}"
            logger.error(error_msg)
            return hostname, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error for {hostname}: {str(e)}"
            logger.error(error_msg)
            return hostname, None, error_msg
    
    def check_all_certificates(self) -> List[Dict]:
        """
        Check certificates for all websites in the configuration
        
        Returns:
            List of results for each website
        """
        websites = self.config.get('websites', [])
        max_workers = self.config.get('max_workers', 5)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.get_certificate_expiry, site['hostname'], site.get('port', 443)): site
                for site in websites
            }
            
            # Process results as they complete
            for future in as_completed(futures):
                site = futures[future]
                hostname, expiry_date, error = future.result()
                
                result = {
                    'hostname': hostname,
                    'port': site.get('port', 443),
                    'expiry_date': expiry_date,
                    'error': error,
                    'days_until_expiry': None,
                    'status': 'ERROR' if error else 'OK'
                }
                
                if expiry_date:
                    days_until_expiry = (expiry_date - datetime.now()).days
                    result['days_until_expiry'] = days_until_expiry
                    
                    # Check thresholds
                    thresholds = self.config.get('thresholds', {})
                    if days_until_expiry <= thresholds.get('critical', 7):
                        result['status'] = 'CRITICAL'
                    elif days_until_expiry <= thresholds.get('warning', 30):
                        result['status'] = 'WARNING'
                    else:
                        result['status'] = 'OK'
                
                self.results.append(result)
        
        return self.results
    
    def display_results(self):
        """Display certificate check results in a human-readable format"""
        print("\n" + "="*80)
        print("SSL/TLS CERTIFICATE EXPIRY CHECK RESULTS")
        print("="*80)
        print(f"Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
        
        for result in self.results:
            hostname = result['hostname']
            port = result['port']
            
            print(f"\nWebsite: {hostname}:{port}")
            print(f"Status: {result['status']}")
            
            if result['error']:
                print(f"Error: {result['error']}")
            else:
                expiry_date = result['expiry_date']
                days_until_expiry = result['days_until_expiry']
                
                # Color coding for terminal output (optional)
                status_symbol = {
                    'OK': '✓',
                    'WARNING': '⚠',
                    'CRITICAL': '✗',
                    'ERROR': '✗'
                }.get(result['status'], '?')
                
                print(f"Certificate Expiry Date: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Days Until Expiry: {days_until_expiry} days {status_symbol}")
                
                if days_until_expiry < 0:
                    print("⚠️  CERTIFICATE HAS EXPIRED!")
        
        print("\n" + "="*80)
    
    def send_alerts(self):
        """Send alerts based on certificate status"""
        alerts_config = self.config.get('alerts', {})
        
        if not alerts_config.get('enabled', False):
            logger.info("Alerts are disabled in configuration")
            return
        
        # Filter results that need alerts
        alert_results = [
            r for r in self.results 
            if r['status'] in ['WARNING', 'CRITICAL', 'ERROR']
        ]
        
        if not alert_results:
            logger.info("No certificates require alerts")
            return
        
        # Send email alerts
        if alerts_config.get('email', {}).get('enabled', False):
            self._send_email_alert(alert_results, alerts_config['email'])
        
        # Send webhook alerts (Slack/Teams)
        if alerts_config.get('webhook', {}).get('enabled', False):
            self._send_webhook_alert(alert_results, alerts_config['webhook'])
    
    def _send_email_alert(self, results: List[Dict], email_config: Dict):
        """
        Send email alerts
        
        Args:
            results: List of results requiring alerts
            email_config: Email configuration
        """
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_config.get('subject', 'SSL Certificate Alert')
            msg['From'] = email_config['from']
            msg['To'] = ', '.join(email_config['to'])
            
            # Create email body
            body = self._create_alert_message(results, 'email')
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                if email_config.get('use_tls', True):
                    server.starttls()
                if email_config.get('username') and email_config.get('password'):
                    server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            
            logger.info("Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_webhook_alert(self, results: List[Dict], webhook_config: Dict):
        """
        Send webhook alerts (Slack/Teams)
        
        Args:
            results: List of results requiring alerts
            webhook_config: Webhook configuration
        """
        try:
            webhook_url = webhook_config['url']
            webhook_type = webhook_config.get('type', 'slack')
            
            if webhook_type == 'slack':
                payload = self._create_slack_payload(results)
            elif webhook_type == 'teams':
                payload = self._create_teams_payload(results)
            else:
                logger.error(f"Unsupported webhook type: {webhook_type}")
                return
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"{webhook_type.capitalize()} webhook alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def _create_alert_message(self, results: List[Dict], format_type: str = 'text') -> str:
        """
        Create alert message
        
        Args:
            results: List of results requiring alerts
            format_type: Message format ('text' or 'email')
            
        Returns:
            Formatted alert message
        """
        if format_type == 'email':
            message = """
            <html>
            <body>
            <h2>SSL Certificate Alert</h2>
            <p>The following certificates require attention:</p>
            <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Website</th>
                <th>Status</th>
                <th>Days Until Expiry</th>
                <th>Expiry Date</th>
                <th>Details</th>
            </tr>
            """
            
            for result in results:
                status_color = {
                    'CRITICAL': '#ff0000',
                    'WARNING': '#ff9900',
                    'ERROR': '#cc0000'
                }.get(result['status'], '#000000')
                
                message += f"""
                <tr>
                    <td>{result['hostname']}:{result['port']}</td>
                    <td style="color: {status_color}; font-weight: bold;">{result['status']}</td>
                    <td>{result.get('days_until_expiry', 'N/A')}</td>
                    <td>{result['expiry_date'].strftime('%Y-%m-%d') if result['expiry_date'] else 'N/A'}</td>
                    <td>{result.get('error', 'Certificate expiring soon')}</td>
                </tr>
                """
            
            message += """
            </table>
            </body>
            </html>
            """
        else:
            message = "SSL Certificate Alert\n\n"
            for result in results:
                message += f"• {result['hostname']}:{result['port']} - {result['status']}\n"
                if result['days_until_expiry'] is not None:
                    message += f"  Days until expiry: {result['days_until_expiry']}\n"
                if result['error']:
                    message += f"  Error: {result['error']}\n"
        
        return message
    
    def _create_slack_payload(self, results: List[Dict]) -> Dict:
        """Create Slack webhook payload"""
        attachments = []
        
        for result in results:
            color = {
                'CRITICAL': 'danger',
                'WARNING': 'warning',
                'ERROR': 'danger'
            }.get(result['status'], '#808080')
            
            fields = [
                {
                    "title": "Website",
                    "value": f"{result['hostname']}:{result['port']}",
                    "short": True
                },
                {
                    "title": "Status",
                    "value": result['status'],
                    "short": True
                }
            ]
            
            if result['days_until_expiry'] is not None:
                fields.append({
                    "title": "Days Until Expiry",
                    "value": str(result['days_until_expiry']),
                    "short": True
                })
            
            if result['error']:
                fields.append({
                    "title": "Error",
                    "value": result['error'],
                    "short": False
                })
            
            attachments.append({
                "color": color,
                "fields": fields,
                "footer": "SSL Certificate Checker",
                "ts": int(datetime.now().timestamp())
            })
        
        return {
            "text": "⚠️ SSL Certificate Alert",
            "attachments": attachments
        }
    
    def _create_teams_payload(self, results: List[Dict]) -> Dict:
        """Create Microsoft Teams webhook payload"""
        sections = []
        
        for result in results:
            facts = [
                {
                    "name": "Website",
                    "value": f"{result['hostname']}:{result['port']}"
                },
                {
                    "name": "Status",
                    "value": result['status']
                }
            ]
            
            if result['days_until_expiry'] is not None:
                facts.append({
                    "name": "Days Until Expiry",
                    "value": str(result['days_until_expiry'])
                })
            
            if result['error']:
                facts.append({
                    "name": "Error",
                    "value": result['error']
                })
            
            sections.append({
                "activityTitle": f"Certificate Alert: {result['hostname']}",
                "facts": facts
            })
        
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "SSL Certificate Alert",
            "themeColor": "FF0000",
            "title": "⚠️ SSL Certificate Alert",
            "sections": sections
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SSL/TLS Certificate Expiry Checker')
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress output (only send alerts)'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        print(f"Error: Configuration file '{args.config}' not found.")
        print("Please create a configuration file with the list of websites to check.")
        sys.exit(1)
    
    try:
        # Initialize and run checker
        checker = CertificateChecker(args.config)
        checker.check_all_certificates()
        
        # Display results unless quiet mode
        if not args.quiet:
            checker.display_results()
        
        # Send alerts if configured
        checker.send_alerts()
        
        # Exit with appropriate code
        critical_count = sum(1 for r in checker.results if r['status'] == 'CRITICAL')
        if critical_count > 0:
            sys.exit(2)  # Critical certificates found
        
        error_count = sum(1 for r in checker.results if r['status'] == 'ERROR')
        if error_count > 0:
            sys.exit(1)  # Errors encountered
        
        sys.exit(0)  # All good
        
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()