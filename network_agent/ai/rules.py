# Danh sách 11 nhãn theo đúng thứ tự huấn luyện (0-10)
CLASS_NAMES = [
    'Streaming', 'VPN-VoIP', 'VPN-chat', 'VPN-email', 'VPN-file_transfer',
    'VPN-p2p', 'VPN-streaming', 'VoIP', 'chat', 'email', 'file_transfer'
]

# --- BỘ TỪ ĐIỂN RULE-BASED THỰC CHIẾN (MỞ RỘNG) ---
SNI_RULES_ADVANCED = {
    # 1. EMAIL
    'mail.google.com': 'email',
    'outlook.live.com': 'email',
    'outlook.office.com': 'email',
    'outlook.office365.com': 'email',
    'smtp': 'email',
    'imap': 'email',
    'pop3': 'email',

    # 2. STREAMING
    'googlevideo.com': 'Streaming',
    'youtube.com': 'Streaming',
    'ytimg.com': 'Streaming',
    'video.xx.fbcdn.net': 'Streaming',
    'nflxvideo.net': 'Streaming',
    'netflix.com': 'Streaming',
    'vimeocdn.com': 'Streaming',
    'ttvnw.net': 'Streaming',
    
    # 3. FILE TRANSFER
    'drive.google.com': 'file_transfer',
    'docs.google.com': 'file_transfer',
    'dropbox.com': 'file_transfer',
    'onedrive.live.com': 'file_transfer',
    'fbsbx.com': 'file_transfer',
    'sharepoint.com': 'file_transfer',
    'mediafire.com': 'file_transfer',
    'mega.nz': 'file_transfer',
}

