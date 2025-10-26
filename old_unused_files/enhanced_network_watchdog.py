#!/usr/bin/env python3
"""
Enhanced Network Watchdog for ZoneSync FX Bot
Monitors network connectivity, API health, and system resources with intelligent recovery
"""

import os
import time
import logging
import subprocess
import psutil
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from robust_notifier import notifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/fxbot/watchdog.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SystemHealthMonitor:
    """Monitor system resources and health"""

    def __init__(self):
        self.cpu_threshold = 90.0  # %
        self.memory_threshold = 90.0  # %
        self.disk_threshold = 90.0  # %

    def check_system_health(self) -> Dict[str, any]:
        """Check various system health metrics"""
        try:
            health = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
                'processes': len(psutil.pids()),
                'healthy': True,
                'issues': []
            }

            # Check thresholds
            if health['cpu_percent'] > self.cpu_threshold:
                health['healthy'] = False
                health['issues'].append(f"High CPU usage: {health['cpu_percent']:.1f}%")

            if health['memory_percent'] > self.memory_threshold:
                health['healthy'] = False
                health['issues'].append(f"High memory usage: {health['memory_percent']:.1f}%")

            if health['disk_percent'] > self.disk_threshold:
                health['healthy'] = False
                health['issues'].append(f"High disk usage: {health['disk_percent']:.1f}%")

            return health

        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {
                'healthy': False,
                'issues': [f"Health check failed: {e}"],
                'error': str(e)
            }

class NetworkConnectivityMonitor:
    """Monitor network connectivity and API health"""

    def __init__(self):
        self.test_endpoints = [
            "https://api.twelvedata.com",
            "https://www.google.com",
            "https://api.telegram.org",
            "https://smtp.gmail.com:465"
        ]
        self.timeout = 10

    def check_network_connectivity(self) -> Dict[str, any]:
        """Test network connectivity to various endpoints"""
        results = {
            'healthy': True,
            'total_tests': len(self.test_endpoints),
            'successful_tests': 0,
            'failed_endpoints': [],
            'response_times': {}
        }

        for endpoint in self.test_endpoints:
            try:
                start_time = time.time()

                if endpoint.startswith('smtp://'):
                    # Special handling for SMTP
                    import socket
                    host, port = endpoint.replace('smtp://', '').split(':')
                    sock = socket.create_connection((host, int(port)), timeout=self.timeout)
                    sock.close()
                    success = True
                else:
                    # HTTP/HTTPS endpoints
                    response = requests.get(endpoint, timeout=self.timeout)
                    success = response.status_code < 500

                response_time = (time.time() - start_time) * 1000

                if success:
                    results['successful_tests'] += 1
                    results['response_times'][endpoint] = response_time
                else:
                    results['failed_endpoints'].append(endpoint)

            except Exception as e:
                logger.warning(f"Network test failed for {endpoint}: {e}")
                results['failed_endpoints'].append(endpoint)

        # Consider network healthy if at least 50% of tests pass
        success_rate = results['successful_tests'] / results['total_tests']
        results['healthy'] = success_rate >= 0.5
        results['success_rate'] = success_rate

        return results

    def check_dns_resolution(self) -> bool:
        """Test DNS resolution"""
        test_domains = ['google.com', 'api.twelvedata.com']

        for domain in test_domains:
            try:
                import socket
                socket.gethostbyname(domain)
                return True
            except socket.gaierror:
                continue

        return False

class ServiceMonitor:
    """Monitor trading bot services and processes"""

    def __init__(self):
        self.services = [
            'fxbot-run.service',
            'fxbot-run.timer',
            'fxbot-net-watchdog.timer'
        ]
        self.process_names = ['python', 'python3']

    def check_systemd_services(self) -> Dict[str, any]:
        """Check status of systemd services"""
        results = {
            'healthy': True,
            'services': {},
            'issues': []
        }

        for service in self.services:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                status = result.stdout.strip()
                results['services'][service] = status

                if status not in ['active', 'activating']:
                    results['healthy'] = False
                    results['issues'].append(f"Service {service} is {status}")

            except subprocess.TimeoutExpired:
                results['healthy'] = False
                results['issues'].append(f"Timeout checking {service}")
            except Exception as e:
                results['healthy'] = False
                results['issues'].append(f"Error checking {service}: {e}")

        return results

    def check_bot_processes(self) -> Dict[str, any]:
        """Check if trading bot processes are running"""
        results = {
            'healthy': False,
            'python_processes': 0,
            'bot_processes': [],
            'issues': []
        }

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] in self.process_names:
                        results['python_processes'] += 1

                        # Check if it's a bot process
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if any(keyword in cmdline.lower() for keyword in ['fxbot', 'trading', 'multi_strategy']):
                            results['bot_processes'].append({
                                'pid': proc.info['pid'],
                                'cmdline': cmdline
                            })

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            results['healthy'] = len(results['bot_processes']) > 0

            if not results['healthy']:
                results['issues'].append("No trading bot processes found")

        except Exception as e:
            results['issues'].append(f"Error checking processes: {e}")

        return results

class EnhancedNetworkWatchdog:
    """Main watchdog class coordinating all monitoring activities"""

    def __init__(self):
        self.system_monitor = SystemHealthMonitor()
        self.network_monitor = NetworkConnectivityMonitor()
        self.service_monitor = ServiceMonitor()
        self.notifier = notifier

        self.consecutive_failures = 0
        self.max_failures = 3
        self.check_interval = 300  # 5 minutes
        self.last_alert_time = {}
        self.alert_cooldown = 3600  # 1 hour

    def run_comprehensive_check(self) -> Dict[str, any]:
        """Run all health checks and return comprehensive results"""
        logger.info("Running comprehensive health check...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'system': self.system_monitor.check_system_health(),
            'network': self.network_monitor.check_network_connectivity(),
            'services': self.service_monitor.check_systemd_services(),
            'processes': self.service_monitor.check_bot_processes(),
            'dns': self.network_monitor.check_dns_resolution(),
            'overall_healthy': True,
            'critical_issues': []
        }

        # Determine overall health
        health_checks = [
            results['system']['healthy'],
            results['network']['healthy'],
            results['services']['healthy'],
            results['processes']['healthy'],
            results['dns']
        ]

        results['overall_healthy'] = all(health_checks)

        # Collect critical issues
        for check_name, check_result in results.items():
            if isinstance(check_result, dict) and not check_result.get('healthy', True):
                issues = check_result.get('issues', [])
                results['critical_issues'].extend(issues)

        return results

    def handle_failures(self, results: Dict[str, any]):
        """Handle detected failures with progressive response"""
        if results['overall_healthy']:
            self.consecutive_failures = 0
            return

        self.consecutive_failures += 1
        logger.warning(f"Health check failed ({self.consecutive_failures}/{self.max_failures})")

        # Log all issues
        for issue in results['critical_issues']:
            logger.error(f"Critical issue: {issue}")

        # Send alert if not in cooldown
        self._send_alert_if_needed('health_check_failed', results)

        # Progressive recovery actions
        if self.consecutive_failures >= self.max_failures:
            logger.critical("Maximum failures reached, attempting recovery actions")
            self._attempt_recovery(results)
            self.consecutive_failures = 0  # Reset after recovery attempt

    def _attempt_recovery(self, results: Dict[str, any]):
        """Attempt various recovery actions based on failure type"""
        logger.info("Attempting system recovery...")

        recovery_actions = []

        # Network issues
        if not results['network']['healthy'] or not results['dns']:
            recovery_actions.extend([
                "sudo systemctl restart systemd-resolved",
                "sudo systemctl restart networking"
            ])

        # Service issues
        if not results['services']['healthy']:
            recovery_actions.extend([
                "sudo systemctl daemon-reload",
                "sudo systemctl restart fxbot-run.timer",
                "sudo systemctl restart fxbot-run.service"
            ])

        # Process issues
        if not results['processes']['healthy']:
            recovery_actions.append("sudo systemctl restart fxbot-run.service")

        # Execute recovery actions
        for action in recovery_actions:
            try:
                logger.info(f"Executing recovery action: {action}")
                result = subprocess.run(
                    action.split(),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"Recovery action successful: {action}")
                else:
                    logger.error(f"Recovery action failed: {action} - {result.stderr}")

                time.sleep(5)  # Wait between actions

            except Exception as e:
                logger.error(f"Error executing recovery action {action}: {e}")

        # Send recovery attempt notification
        self._send_alert_if_needed('recovery_attempted', {
            'actions': recovery_actions,
            'timestamp': datetime.now().isoformat()
        })

        # Final option: system reboot if critical
        if results['system']['healthy'] == False and len(results['critical_issues']) > 5:
            logger.critical("System severely compromised, scheduling reboot in 5 minutes")
            self._send_alert_if_needed('system_reboot_scheduled', {
                'reason': 'Critical system health issues',
                'reboot_time': (datetime.now() + timedelta(minutes=5)).isoformat()
            })

            # Schedule reboot
            subprocess.run(['sudo', 'shutdown', '-r', '+5'], capture_output=True)

    def _send_alert_if_needed(self, alert_type: str, data: Dict[str, any]):
        """Send alert if not in cooldown period"""
        current_time = time.time()
        last_alert = self.last_alert_time.get(alert_type, 0)

        if current_time - last_alert > self.alert_cooldown:
            self.last_alert_time[alert_type] = current_time

            if alert_type == 'health_check_failed':
                message = f"Health Check Failed\n\nCritical Issues:\n" + \
                         "\n".join(f"- {issue}" for issue in data.get('critical_issues', []))

            elif alert_type == 'recovery_attempted':
                message = f"Recovery Actions Attempted\n\nActions:\n" + \
                         "\n".join(f"- {action}" for action in data.get('actions', []))

            elif alert_type == 'system_reboot_scheduled':
                message = f"System Reboot Scheduled\n\nReason: {data.get('reason', 'Unknown')}\n" + \
                         f"Scheduled Time: {data.get('reboot_time', 'Unknown')}"

            else:
                message = f"Watchdog Alert: {alert_type}\n\nData: {data}"

            self.notifier.send_system_alert(
                alert_level="critical" if "reboot" in alert_type else "warning",
                component="Network Watchdog",
                message=message
            )

    def run_forever(self):
        """Main watchdog loop"""
        logger.info("Enhanced Network Watchdog starting...")

        while True:
            try:
                results = self.run_comprehensive_check()
                self.handle_failures(results)

                if results['overall_healthy']:
                    logger.info("All systems healthy")
                else:
                    logger.warning(f"Issues detected: {len(results['critical_issues'])} critical issues")

            except KeyboardInterrupt:
                logger.info("Watchdog stopped by user")
                break

            except Exception as e:
                logger.error(f"Watchdog error: {e}")
                time.sleep(60)  # Wait before retrying

            time.sleep(self.check_interval)

    def generate_health_report(self) -> str:
        """Generate detailed health report"""
        results = self.run_comprehensive_check()

        report = f"""
=== ZoneSync FX Bot Health Report ===
Generated: {results['timestamp']}

Overall Status: {'HEALTHY' if results['overall_healthy'] else 'UNHEALTHY'}

System Health:
- CPU Usage: {results['system'].get('cpu_percent', 'N/A'):.1f}%
- Memory Usage: {results['system'].get('memory_percent', 'N/A'):.1f}%
- Disk Usage: {results['system'].get('disk_percent', 'N/A'):.1f}%

Network Health:
- Connectivity: {'OK' if results['network']['healthy'] else 'ISSUES'}
- Success Rate: {results['network'].get('success_rate', 0):.1%}
- DNS Resolution: {'OK' if results['dns'] else 'FAILED'}

Services:
{chr(10).join(f"- {service}: {status}" for service, status in results['services'].get('services', {}).items())}

Processes:
- Bot Processes: {len(results['processes'].get('bot_processes', []))}
- Python Processes: {results['processes'].get('python_processes', 0)}

Critical Issues:
{chr(10).join(f"- {issue}" for issue in results['critical_issues']) if results['critical_issues'] else "None"}
        """.strip()

        return report


if __name__ == "__main__":
    # Run watchdog when executed directly
    watchdog = EnhancedNetworkWatchdog()

    # If --report flag, generate report and exit
    if len(os.sys.argv) > 1 and '--report' in os.sys.argv:
        print(watchdog.generate_health_report())
    else:
        # Run continuous monitoring
        watchdog.run_forever()