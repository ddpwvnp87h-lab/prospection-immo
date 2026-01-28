"""
Profils de headers pour différents navigateurs.
Basé sur l'analyse de vrais navigateurs via developer tools.
"""

# Chrome 120 sur macOS - Profil le plus courant
CHROME_120_MACOS = {
    'name': 'Chrome 120 macOS',
    'base': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    },
    'same_origin': {
        'Sec-Fetch-Site': 'same-origin',
    },
    'cross_site': {
        'Sec-Fetch-Site': 'cross-site',
    }
}

# Chrome 120 sur Windows
CHROME_120_WINDOWS = {
    'name': 'Chrome 120 Windows',
    'base': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    },
    'same_origin': {
        'Sec-Fetch-Site': 'same-origin',
    }
}

# Chrome 119 sur macOS (variation)
CHROME_119_MACOS = {
    'name': 'Chrome 119 macOS',
    'base': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    },
    'same_origin': {
        'Sec-Fetch-Site': 'same-origin',
    }
}

# Firefox 121 sur macOS
FIREFOX_121_MACOS = {
    'name': 'Firefox 121 macOS',
    'base': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Firefox n'envoie PAS sec-ch-ua (c'est un signal Chrome)
    },
    'same_origin': {
        'Sec-Fetch-Site': 'same-origin',
    }
}

# Safari 17 sur macOS
SAFARI_17_MACOS = {
    'name': 'Safari 17 macOS',
    'base': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'fr-FR,fr;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        # Safari n'envoie pas les sec-ch-ua ni Sec-Fetch-*
    },
    'same_origin': {}
}

# Pool de profils pour rotation
BROWSER_PROFILES = [
    CHROME_120_MACOS,
    CHROME_120_WINDOWS,
    CHROME_119_MACOS,
    FIREFOX_121_MACOS,
    SAFARI_17_MACOS,
]

# Referers réalistes par site
REFERERS = {
    'default': [
        'https://www.google.fr/',
        'https://www.google.com/',
        'https://www.google.fr/search?q=immobilier',
        'https://www.google.fr/search?q=maison+a+vendre',
        'https://www.google.fr/search?q=appartement+particulier',
    ],
    'pap.fr': [
        'https://www.google.fr/search?q=pap+immobilier',
        'https://www.google.fr/search?q=pap+particulier',
        'https://www.google.fr/',
    ],
    'leboncoin.fr': [
        'https://www.google.fr/search?q=leboncoin+immobilier',
        'https://www.google.fr/search?q=leboncoin+maison',
        'https://www.google.fr/',
    ],
    'paruvendu.fr': [
        'https://www.google.fr/search?q=paruvendu+immobilier',
        'https://www.google.fr/',
    ],
}
