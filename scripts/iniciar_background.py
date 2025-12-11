"""
Iniciar Modo 24/7 em Background (Windows)

Este script permite rodar o sistema 24/7 sem bloquear o terminal.
Cria um processo separado que continua rodando mesmo se você fechar a janela.

Uso:
    python scripts\iniciar_background.py                # Rodar indefinidamente
    python scripts\iniciar_background.py --hours 48     # Rodar 48 horas
    python scripts\iniciar_background.py --task-scheduler  # Via Task Scheduler
"""

import subprocess
import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackgroundRunner:
    """Gerencia execução em background no Windows"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent.parent
        self.venv_python = self.project_dir / 'venv' / 'Scripts' / 'python.exe'
        self.script = self.project_dir / 'scripts' / 'modo_24_7.py'
        self.log_file = self.project_dir / 'logs' / 'background_24_7.log'
        
        # Criar log directory se não existir
        self.log_file.parent.mkdir(exist_ok=True)
    
    def run_detached(self, hours=0):
        """Rodar em processo separado (detached)"""
        logger.info("="*80)
        logger.info("INICIANDO MODO 24/7 EM BACKGROUND")
        logger.info("="*80)
        
        # Preparar comando
        cmd = [
            'powershell.exe',
            '-NoExit',
            '-Command',
            f'cd \'{self.project_dir}\'; '
            f'.\\venv\\Scripts\\Activate.ps1; '
        ]
        
        if hours > 0:
            cmd.append(f'python scripts\\modo_24_7.py --duration {hours}')
            logger.info(f"Duração: {hours} hora(s)")
        else:
            cmd.append('python scripts\\modo_24_7.py')
            logger.info("Duração: Indefinido (24/7)")
        
        try:
            # Executar em novo processo sem bloquear
            subprocess.Popen(
                ' '.join(cmd),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            logger.info("✅ Processo iniciado com sucesso!")
            logger.info(f"PID: Novo window será criada")
            logger.info(f"Log: {self.log_file}")
            logger.info("\n💡 Dicas:")
            logger.info("   1. Deixe a janela aberta para o sistema continuar rodando")
            logger.info("   2. Feche a janela para parar o sistema")
            logger.info("   3. Para deixar rodando em background, veja opção Task Scheduler")
            
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar: {str(e)}")
            return False
    
    def install_task_scheduler(self, hours=0):
        """Instalar como tarefa agendada no Windows Task Scheduler"""
        logger.info("="*80)
        logger.info("INSTALANDO NO TASK SCHEDULER")
        logger.info("="*80)
        
        task_name = "Modo247_BetAnalysis"
        
        if hours > 0:
            cmd = f'python.exe scripts\\modo_24_7.py --duration {hours}'
            logger.info(f"Duração: {hours} hora(s)")
        else:
            cmd = 'python.exe scripts\\modo_24_7.py'
            logger.info("Duração: Indefinido (reinicia ao inicializar PC)")
        
        # Criar script PowerShell para Task Scheduler
        ps_script = f"""
# Tarefa para Modo 24/7
$action = New-ScheduledTaskAction -Execute "{self.venv_python}" -Argument "{cmd}" -WorkingDirectory "{self.project_dir}"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force

Write-Host "✅ Tarefa '{task_name}' instalada com sucesso!"
Write-Host "   A tarefa rodará automaticamente ao inicializar o PC"
Write-Host "   Para gerenciar: taskschd.msc"
"""
        
        ps_file = self.project_dir / 'install_task.ps1'
        with open(ps_file, 'w') as f:
            f.write(ps_script)
        
        logger.info(f"\n📝 Script criado: {ps_file}")
        logger.info("\nPara instalar, execute como ADMIN:")
        logger.info(f"  powershell -ExecutionPolicy Bypass -File \"{ps_file}\"")
        logger.info("\nOu execute manualmente:")
        logger.info("  1. Abra 'Task Scheduler'")
        logger.info("  2. Create Basic Task...")
        logger.info(f"  3. Nome: {task_name}")
        logger.info("  4. Trigger: At startup")
        logger.info(f"  5. Action: Execute Python script")
        
        return str(ps_file)
    
    def list_processes(self):
        """Listar processos Python em execução"""
        logger.info("="*80)
        logger.info("PROCESSOS PYTHON ATIVOS")
        logger.info("="*80)
        
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 3:  # Header + separator + pelo menos 1 processo
                logger.info(result.stdout)
                logger.info("\nPara matar um processo:")
                logger.info("  taskkill /PID [PID]")
            else:
                logger.info("Nenhum processo Python ativo")
        except Exception as e:
            logger.error(f"Erro ao listar processos: {str(e)}")
    
    def stop_all(self):
        """Parar todos os processos modo_24_7.py"""
        logger.info("="*80)
        logger.info("PARANDO TODOS OS PROCESSOS")
        logger.info("="*80)
        
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                capture_output=True,
                text=True
            )
            
            if 'python.exe' in result.stdout:
                logger.info("Parando processos Python...")
                subprocess.run(['taskkill', '/IM', 'python.exe', '/F'])
                logger.info("✅ Processos paraliados")
            else:
                logger.info("Nenhum processo ativo para parar")
        except Exception as e:
            logger.error(f"Erro: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description='Executar Modo 24/7 em background'
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--hours',
        type=int,
        default=0,
        help='Duração em horas (0=indefinido)'
    )
    group.add_argument(
        '--task-scheduler',
        action='store_true',
        help='Instalar no Task Scheduler (roda ao inicializar PC)'
    )
    group.add_argument(
        '--list',
        action='store_true',
        help='Listar processos ativos'
    )
    group.add_argument(
        '--stop',
        action='store_true',
        help='Parar todos os processos'
    )
    
    args = parser.parse_args()
    
    runner = BackgroundRunner()
    
    if args.list:
        runner.list_processes()
    elif args.stop:
        runner.stop_all()
    elif args.task_scheduler:
        ps_file = runner.install_task_scheduler(args.hours)
        logger.info(f"\n📋 Para completar a instalação, abra PowerShell como ADMIN e execute:")
        logger.info(f"   powershell -ExecutionPolicy Bypass -File \"{ps_file}\"")
    else:
        runner.run_detached(args.hours)

if __name__ == '__main__':
    main()
