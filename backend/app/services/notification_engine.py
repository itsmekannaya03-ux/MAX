import asyncio
import subprocess
import os
import platform
from typing import List, Dict, Any, Callable
from datetime import datetime

class NotificationEngine:
    def __init__(self):
        self.listeners: List[Callable[[Dict[str, Any]], Any]] = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], Any]):
        self.listeners.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], Any]):
        if callback in self.listeners:
            self.listeners.remove(callback)

    async def broadcast(self, payload: Dict[str, Any]):
        """Sends real-time notification to all connected WebSocket clients."""
        for cb in list(self.listeners):
            try:
                res = cb(payload)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as e:
                print(f"[NotificationEngine] Broadcast listener error: {e}")

    async def send_desktop_notification(self, title: str, message: str, category: str = "reminder"):
        """
        Dispatches native OS notification on Windows and broadcasts over WebSocket.
        """
        payload = {
            "type": "notification",
            "title": title,
            "message": message,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Broadcast to frontend WebSocket
        await self.broadcast(payload)

        # 2. Windows Native Toast / Tray Notification
        if platform.system() == "Windows":
            try:
                # Use clean PowerShell toast notification without blocking
                ps_script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $toastXml = [xml]$template.GetXml()
                $textNodes = $toastXml.GetElementsByTagName("text")
                $textNodes.Item(0).AppendChild($toastXml.CreateTextNode('{title}')) > $null
                $textNodes.Item(1).AppendChild($toastXml.CreateTextNode('{message}')) > $null
                $toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('MAX Assistant').Show($toast)
                """
                # Run async without hanging
                asyncio.create_task(self._run_powershell_toast(title, message))
            except Exception as e:
                print(f"[NotificationEngine] Desktop toast error: {e}")

    async def _run_powershell_toast(self, title: str, message: str):
        try:
            # Safe escaped strings
            safe_title = title.replace("'", "''").replace('"', '`"')
            safe_msg = message.replace("'", "''").replace('"', '`"')
            cmd = f'powershell -Command "[reflection.assembly]::loadwithpartialname(\'System.Windows.Forms\') | Out-Null; [System.Windows.Forms.MessageBox]::Show(\'{safe_msg}\', \'{safe_title}\')"'
            # Alternatively use Windows notification balloon via powershell:
            balloon_cmd = f'''powershell -WindowStyle Hidden -Command "$wshell = New-Object -ComObject Wscript.Shell; $wshell.Popup('{safe_msg}', 4, '{safe_title}', 64)"'''
            subprocess.Popen(balloon_cmd, shell=True)
        except Exception as e:
            pass

notification_engine = NotificationEngine()

