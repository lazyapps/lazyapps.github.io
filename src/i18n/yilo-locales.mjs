import copy from './yilo-short-copy.json' with { type: 'json' };

// Shared page labels. Product descriptions also feed the Press Kit catalog.
const labels = {
  "zh-hans": {
    "htmlLang": "zh-Hans",
    "navAria": "主导航",
    "homeAria": "首页",
    "localeNow": "简体中文",
    "selectAria": "切换语言",
    "cta": [
      "下载 Mac 版",
      "iPhone 公开测试版",
      "查看更新记录"
    ],
    "next": {
      "imgAlt": "亦言 App 图标",
      "q": "<span class=\"zh\">下载 Mac 版</span>"
    },
    "brew": {
      "h3": "<span class=\"zh\">通过 Homebrew 安装</span>",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "ar": {
    "htmlLang": "ar",
    "htmlDir": "rtl",
    "navAria": "التنقل الرئيسي",
    "homeAria": "الرئيسية",
    "localeNow": "العربية",
    "selectAria": "تغيير اللغة",
    "cta": [
      "تنزيل نسخة Mac",
      "نسخة iPhone التجريبية",
      "سجل التحديثات"
    ],
    "next": {
      "imgAlt": "أيقونة تطبيق Yilo",
      "q": "تنزيل نسخة Mac"
    },
    "brew": {
      "h3": "التثبيت باستخدام Homebrew",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "de": {
    "htmlLang": "de",
    "navAria": "Hauptnavigation",
    "homeAria": "Start",
    "localeNow": "Deutsch",
    "selectAria": "Sprache wechseln",
    "cta": [
      "Für Mac laden",
      "iPhone-Beta",
      "Änderungen ansehen"
    ],
    "next": {
      "imgAlt": "Yilo-App-Symbol",
      "q": "Für Mac laden"
    },
    "brew": {
      "h3": "Mit Homebrew installieren",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "en": {
    "htmlLang": "en",
    "navAria": "Main navigation",
    "homeAria": "Home",
    "localeNow": "English",
    "selectAria": "Change language",
    "cta": [
      "Download for Mac",
      "iPhone public beta",
      "Release notes"
    ],
    "next": {
      "imgAlt": "Yilo app icon",
      "q": "Download for Mac"
    },
    "brew": {
      "h3": "Install with Homebrew",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "es": {
    "htmlLang": "es",
    "navAria": "Navegación principal",
    "homeAria": "Inicio",
    "localeNow": "Español",
    "selectAria": "Cambiar de idioma",
    "cta": [
      "Descargar para Mac",
      "Beta pública para iPhone",
      "Notas de la versión"
    ],
    "next": {
      "imgAlt": "Icono de Yilo",
      "q": "Descargar para Mac"
    },
    "brew": {
      "h3": "Instalar con Homebrew",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "fr": {
    "htmlLang": "fr",
    "navAria": "Navigation principale",
    "homeAria": "Accueil",
    "localeNow": "Français",
    "selectAria": "Changer de langue",
    "cta": [
      "Télécharger pour Mac",
      "Bêta publique iPhone",
      "Notes de version"
    ],
    "next": {
      "imgAlt": "Icône de Yilo",
      "q": "Télécharger pour Mac"
    },
    "brew": {
      "h3": "Installer avec Homebrew",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "hi": {
    "htmlLang": "hi",
    "navAria": "मुख्य नेविगेशन",
    "homeAria": "मुख्य पृष्ठ",
    "localeNow": "हिन्दी",
    "selectAria": "भाषा बदलें",
    "cta": [
      "Mac के लिए डाउनलोड",
      "iPhone सार्वजनिक बीटा",
      "अपडेट सूची देखें"
    ],
    "next": {
      "imgAlt": "Yilo ऐप आइकन",
      "q": "Mac के लिए डाउनलोड"
    },
    "brew": {
      "h3": "Homebrew से इंस्टॉल करें",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "ja": {
    "htmlLang": "ja",
    "navAria": "メインナビゲーション",
    "homeAria": "ホーム",
    "localeNow": "日本語",
    "selectAria": "言語を切り替える",
    "cta": [
      "Mac 版をダウンロード",
      "iPhone 版パブリックベータ",
      "更新履歴を見る"
    ],
    "next": {
      "imgAlt": "Yiloのアプリアイコン",
      "q": "Mac 版をダウンロード"
    },
    "brew": {
      "h3": "Homebrewでインストール",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "ko": {
    "htmlLang": "ko",
    "navAria": "주요 내비게이션",
    "homeAria": "홈",
    "localeNow": "한국어",
    "selectAria": "언어 변경",
    "cta": [
      "Mac 버전 다운로드",
      "iPhone 공개 베타",
      "업데이트 기록 보기"
    ],
    "next": {
      "imgAlt": "Yilo 앱 아이콘",
      "q": "Mac 버전 다운로드"
    },
    "brew": {
      "h3": "Homebrew로 설치",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "pt-br": {
    "htmlLang": "pt-BR",
    "navAria": "Navegação principal",
    "homeAria": "Início",
    "localeNow": "Português",
    "selectAria": "Mudar de idioma",
    "cta": [
      "Baixar para Mac",
      "Beta pública para iPhone",
      "Notas da versão"
    ],
    "next": {
      "imgAlt": "Ícone do Yilo",
      "q": "Baixar para Mac"
    },
    "brew": {
      "h3": "Instalar com Homebrew",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "ru": {
    "htmlLang": "ru",
    "navAria": "Основная навигация",
    "homeAria": "Главная",
    "localeNow": "Русский",
    "selectAria": "Сменить язык",
    "cta": [
      "Скачать для Mac",
      "Открытая бета для iPhone",
      "Список изменений"
    ],
    "next": {
      "imgAlt": "Значок приложения Yilo",
      "q": "Скачать для Mac"
    },
    "brew": {
      "h3": "Установка через Homebrew",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  },
  "zh-hant": {
    "htmlLang": "zh-Hant",
    "navAria": "主導覽",
    "homeAria": "首頁",
    "localeNow": "繁體中文",
    "selectAria": "切換語言",
    "cta": [
      "下載 Mac 版",
      "iPhone 公開測試版",
      "查看更新記錄"
    ],
    "next": {
      "imgAlt": "亦言 App 圖示",
      "q": "<span class=\"zh\">下載 Mac 版</span>"
    },
    "brew": {
      "h3": "<span class=\"zh\">透過 Homebrew 安裝</span>",
      "label": "Homebrew",
      "install": "<span class=\"p\">$</span> brew tap cxa/yilo https://github.com/cxa/yilo\n<span class=\"p\">$</span> brew install --cask cxa/yilo/yiyan"
    }
  }
};
export const YILO_LOCALES = Object.fromEntries(Object.entries(labels).map(([code, labels]) => {
  const text = copy[code];
  const url = '/yilo/' + (code === 'en' ? '' : code + '/');
  return [code, { ...labels, title: text.title, description: text.sub, sub: text.sub,
    ogTitle: text.title, ogDesc: text.sub, canonical: 'https://lazyapps.com' + url,
    selectedUrl: url, appTitle: code === 'zh-hans' || code === 'zh-hant' ? '亦言' : 'Yilo',
    loaderLogo: 'YILO', h1: text.headline, formerName: text.formerName }];
}));
