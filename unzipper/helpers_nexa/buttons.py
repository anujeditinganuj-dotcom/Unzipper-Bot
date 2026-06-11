# ===================================================================== #
#  Modified: Src-bot emojis + ButtonStyle + Wallhaven start integration #
# ===================================================================== #

from os.path import basename
from unzipper.client.caching import STRINGS
from unzipper.helpers_nexa.utils import read_json_sync
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

try:
    from pyrogram.enums import ButtonStyle
    BUTTON_STYLE_SUPPORTED = True
except ImportError:
    BUTTON_STYLE_SUPPORTED = False

# =========================================================
# Custom Premium Emoji IDs  (from Src-bot)
# =========================================================
E_WARN    = '<emoji id=5447644880824181073>⚠️</emoji>'
E_INFO    = '<emoji id=5334544901428229844>ℹ️</emoji>'
E_CROWN   = '<emoji id=5217822164362739968>👑</emoji>'
E_SPARK   = '<emoji id=5325547803936572038>✨</emoji>'
E_CHECK   = '<emoji id=5206607081334906820>✔️</emoji>'
E_BOLT    = '<emoji id=5456140674028019486>⚡️</emoji>'
E_GEAR    = '<emoji id=5341715473882955310>⚙️</emoji>'
E_STAR    = '<emoji id=5438496463044752972>⭐️</emoji>'
E_STOP    = '<emoji id=5260293700088511294>⛔️</emoji>'
E_GREEN   = '<emoji id=5416081784641168838>🟢</emoji>'
E_RED     = '<emoji id=5411225014148014586>🔴</emoji>'
E_LINK    = '<emoji id=5271604874419647061>🔗</emoji>'
E_BATCH   = '<emoji id=5341498088408234504>💯</emoji>'
E_PENCIL  = '<emoji id=5395444784611480792>✏️</emoji>'
E_TIP     = '<emoji id=5422439311196834318>💡</emoji>'
E_IMAGE   = '<emoji id=5395444784611480792>🖼</emoji>'
E_STATS   = '<emoji id=5334544901428229844>📊</emoji>'
E_PAYMENT = '<emoji id=5325547803936572038>💳</emoji>'
E_CHANNEL = '<emoji id=5271604874419647061>📢</emoji>'
E_DEV     = '<emoji id=5217822164362739968>👨‍💻</emoji>'
E_CROSS   = '<emoji id=5210952531676504517>❌</emoji>'
E_LOCK    = '<emoji id=5296369303661067030>🔒</emoji>'
E_DIAMOND = '<emoji id=5217822164362739968>💎</emoji>'
E_ROCKET  = '<emoji id=5456140674028019486>🚀</emoji>'
E_SHIELD  = '<emoji id=5251203410396458957>🛡</emoji>'
E_CLOCK   = '<emoji id=5386367538735104399>⌛</emoji>'
E_ARROW   = '<emoji id=5416117059207572332>➡️</emoji>'

# =========================================================
# Button Icon IDs  (from Src-bot)
# =========================================================
ICON_INFO      = 5334544901428229844
ICON_WARN      = 5447644880824181073
ICON_HELP      = 5443038326535759644
ICON_DEV       = 5823268688874179761
ICON_BACK      = 5447183459602669338
ICON_GEAR      = 5341715473882955310
ICON_PENCIL    = 5395444784611480792
ICON_TRASH     = 5260293700088511294
ICON_REFRESH   = 5375338737028841420
ICON_PREMIUM   = 5217822164362739968
ICON_PAYMENT   = 5325547803936572038
ICON_IMAGE     = 5395444784611480792
ICON_STATS     = 5334544901428229844
ICON_CHANNEL   = 5271604874419647061
ICON_CLOSE     = 5210952531676504517
ICON_HOME      = 5447183459602669338
ICON_LIST      = 5334544901428229844
ICON_ARCHIVE   = 5341498088408234504
ICON_UPLOAD    = 5325547803936572038
ICON_DOWNLOAD  = 5456140674028019486
ICON_PASS      = 5296369303661067030
ICON_CANCEL    = 5210952531676504517
ICON_LANG      = 5271604874419647061
ICON_THUMB     = 5395444784611480792
ICON_BACKUP    = 5334544901428229844
ICON_CHECK     = 5206607081334906820


# =========================================================
# Safe button builder (with ButtonStyle if supported)
# =========================================================
import re as _re

def _strip_emoji_tags(text: str) -> str:
    """Remove <emoji id=...>fallback</emoji> tags, keep only the fallback emoji."""
    return _re.sub(r'<emoji id=\d+>(.*?)</emoji>', r'\1', text).strip()


def make_btn(text, callback_data=None, url=None,
             icon_custom_emoji_id=None, style=None):
    if not BUTTON_STYLE_SUPPORTED:
        # Strip <emoji> tags → plain fallback emoji in button text
        text = _strip_emoji_tags(text)

    kwargs = {"text": text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if BUTTON_STYLE_SUPPORTED:
        if icon_custom_emoji_id:
            kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
        if style is not None:
            kwargs["style"] = style
    # When not supported: skip icon_custom_emoji_id and style entirely
    return InlineKeyboardButton(**kwargs)


def _P():
    """Return ButtonStyle.PRIMARY or None"""
    if BUTTON_STYLE_SUPPORTED:
        return ButtonStyle.PRIMARY
    return None

def _D():
    """Return ButtonStyle.DANGER or None"""
    if BUTTON_STYLE_SUPPORTED:
        return ButtonStyle.DANGER
    return None

def _S():
    """Return ButtonStyle.SUCCESS or None"""
    if BUTTON_STYLE_SUPPORTED:
        return ButtonStyle.SUCCESS
    return None


# =========================================================
class Unzipper_Buttons:
    def __init__(self) -> None:
        pass

    async def make_button(self, text: str, *args, **kwargs):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text, *args, **kwargs)]
        ])

    async def make_files_keyboard(self, files: list, user_id: int, chat_id: int, inlude_files: bool = True):
        # Top row: Upload All + Cancel side by side
        rows = [[
            make_btn(f"{E_BATCH} {STRINGS['buttons']['upload_all']}", callback_data=f"ext_a|{user_id}|{chat_id}", icon_custom_emoji_id=ICON_ARCHIVE, style=_P()),
            make_btn(f"{E_CROSS} {STRINGS['buttons']['cancel']}",     callback_data="cancel_dis",                  icon_custom_emoji_id=ICON_CANCEL,  style=_D()),
        ]]
        if inlude_files:
            file_btns = []
            for num, file in enumerate(files):
                if num >= 90:
                    break
                file_btns.append(
                    InlineKeyboardButton(
                        f"{num} - {basename(file)}".encode("utf-8").decode("utf-8"),
                        callback_data=f"ext_f|{user_id}|{chat_id}|{num}"
                    )
                )
            # Pair file buttons into rows of 2
            for i in range(0, len(file_btns), 2):
                rows.append(file_btns[i:i+2])
        return InlineKeyboardMarkup(rows)

    # ── Static keyboards ──────────────────────────────────────────────

    @property
    def START(self):
        return InlineKeyboardMarkup([
            [
                make_btn(f" {E_INFO} ʜᴇʟᴘ ",     callback_data="helpcallback",     icon_custom_emoji_id=ICON_HELP,  style=_P()),
                make_btn(f" {E_BOLT} ᴀʙᴏᴜᴛ ",    callback_data="aboutcallback",    icon_custom_emoji_id=ICON_INFO,  style=_P()),
            ],
            [
                make_btn(f" {E_GEAR} sᴇᴛᴛɪɴɢs ", callback_data="settingscallback", icon_custom_emoji_id=ICON_GEAR,  style=_P()),
                make_btn(f" {E_SHIELD} ʀᴜʟᴇs ",  callback_data="rulescallback",    icon_custom_emoji_id=ICON_LIST,  style=_P()),
            ],
        ])

    @property
    def HELP(self):
        return InlineKeyboardMarkup([
            [
                make_btn(f" {E_BATCH} ᴇxᴛʀᴀᴄᴛ ",   callback_data="extracthelp", icon_custom_emoji_id=ICON_ARCHIVE, style=_P()),
                make_btn(f" {E_BOLT} ᴜᴘʟᴏᴀᴅ ",      callback_data="upmodhelp",   icon_custom_emoji_id=ICON_UPLOAD,  style=_P()),
            ],
            [
                make_btn(f" {E_IMAGE} ᴛʜᴜᴍʙɴᴀɪʟ ", callback_data="thumbhelp",   icon_custom_emoji_id=ICON_THUMB,   style=_P()),
                make_btn(f" {E_STATS} ʙᴀᴄᴋᴜᴘ ",    callback_data="backuphelp",  icon_custom_emoji_id=ICON_BACKUP,  style=_P()),
            ],
            [
                make_btn(f" {E_CHANNEL} ʟᴀɴɢᴜᴀɢᴇs ", callback_data="langhelp", icon_custom_emoji_id=ICON_LANG,  style=_P()),
            ],
            [
                make_btn(f" {E_ARROW} ʙᴀᴄᴋ ", callback_data="megoinhome", icon_custom_emoji_id=ICON_HOME, style=_D()),
            ],
        ])

    @property
    def HELP_BACK(self):
        return InlineKeyboardMarkup([[
            make_btn(f" {E_ARROW} ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ ", callback_data="helpcallback", icon_custom_emoji_id=ICON_HOME, style=_P()),
        ]])

    @property
    def EXTRACT_FILE(self):
        return InlineKeyboardMarkup([
            [make_btn(f" {E_BATCH} ꜰɪʟᴇ ᴇxᴛʀᴀᴄᴛ ",          callback_data="extract_file|tg_file|no_pass",   icon_custom_emoji_id=ICON_ARCHIVE,  style=_P())],
            [make_btn(f" {E_LOCK} ꜰɪʟᴇ (ᴘᴀssᴡᴏʀᴅ) ᴇxᴛʀᴀᴄᴛ ", callback_data="extract_file|tg_file|with_pass", icon_custom_emoji_id=ICON_PASS,     style=_P())],
            [make_btn(f" {E_CROSS} ᴄᴀɴᴄᴇʟ ",                  callback_data="cancel_dis",                     icon_custom_emoji_id=ICON_CANCEL,   style=_D())],
        ])

    @property
    def EXTRACT_URL(self):
        return InlineKeyboardMarkup([
            [make_btn(f" {E_LINK} ᴜʀʟ ᴇxᴛʀᴀᴄᴛ ",              callback_data="extract_file|url|no_pass",   icon_custom_emoji_id=ICON_DOWNLOAD, style=_P())],
            [make_btn(f" {E_LOCK} (ᴘᴀssᴡᴏʀᴅ) ᴜʀʟ ᴇxᴛʀᴀᴄᴛ ", callback_data="extract_file|url|with_pass", icon_custom_emoji_id=ICON_PASS,     style=_P())],
            [make_btn(f" {E_CROSS} ᴄᴀɴᴄᴇʟ ",                   callback_data="cancel_dis",                 icon_custom_emoji_id=ICON_CANCEL,   style=_D())],
        ])

    @property
    def CLEAN(self):
        return InlineKeyboardMarkup([
            [make_btn(f" {E_STOP} ᴄʟᴇᴀɴ ᴍʏ ꜰɪʟᴇs ", callback_data="cancel_dis", icon_custom_emoji_id=ICON_TRASH,  style=_D())],
            [make_btn(f" {E_SPARK} ɴᴏᴏᴏ 😳! ",        callback_data="nobully",    icon_custom_emoji_id=ICON_CHECK,  style=_S())],
        ])

    @property
    def BACKUP(self):
        return InlineKeyboardMarkup([[
            make_btn(" Gofile.io ", callback_data="cloudbackup|gofile", icon_custom_emoji_id=ICON_BACKUP, style=_P()),
        ]])

    @property
    def SETTINGS_GOFILE(self):
        return InlineKeyboardMarkup([
            [
                make_btn(f" {E_PENCIL} sᴇᴛ ᴛᴏᴋᴇɴ ",    callback_data="gf_setting-set", icon_custom_emoji_id=ICON_PENCIL, style=_P()),
                make_btn(f" {E_CROSS} ᴅᴇʟ ᴛᴏᴋᴇɴ ",     callback_data="gf_setting-del", icon_custom_emoji_id=ICON_CANCEL, style=_D()),
            ],
            [make_btn(f" {E_INFO} ɢᴇᴛ ᴛᴏᴋᴇɴ ", callback_data="gf_setting-get", icon_custom_emoji_id=ICON_INFO, style=_P())],
        ])

    @property
    def UPLOAD_MODE(self):
        return InlineKeyboardMarkup([
            [make_btn(f" {E_STATS} ᴀs ᴅᴏᴄ 📁 ",   callback_data="set_mode|doc",   icon_custom_emoji_id=ICON_ARCHIVE, style=_P())],
            [make_btn(f" {E_BOLT} ᴀs ᴠɪᴅᴇᴏ 📹 ",  callback_data="set_mode|video", icon_custom_emoji_id=ICON_UPLOAD,  style=_P())],
        ])

    @property
    def LANGUAGES(self):
        return InlineKeyboardMarkup([
            [make_btn(v, callback_data=f"set_lang|{k}", icon_custom_emoji_id=ICON_LANG, style=_P())]
            for k, v in read_json_sync("unzipper/localization/languages.json", True)
        ])

    @property
    def SETTINGS(self):
        return InlineKeyboardMarkup([
            [
                make_btn(f" {E_BOLT} ᴜᴘʟᴏᴀᴅ ᴍᴏᴅᴇ ", callback_data="uploadmodecallback", icon_custom_emoji_id=ICON_UPLOAD, style=_P()),
            ],
            [
                make_btn(f" {E_IMAGE} ᴛʜᴜᴍʙɴᴀɪʟ ",  callback_data="thumbcallback",       icon_custom_emoji_id=ICON_THUMB,  style=_P()),
                make_btn(f" {E_CHANNEL} ʟᴀɴɢᴜᴀɢᴇ ", callback_data="langcallback",        icon_custom_emoji_id=ICON_LANG,   style=_P()),
            ],
            [
                make_btn(f" {E_ARROW} ʙᴀᴄᴋ ", callback_data="megoinhome", icon_custom_emoji_id=ICON_HOME, style=_D()),
            ],
        ])

    @property
    def BACK(self):
        return InlineKeyboardMarkup([[
            make_btn(f" {E_ARROW} ʙᴀᴄᴋ ", callback_data="megoinhome", icon_custom_emoji_id=ICON_HOME, style=_D()),
        ]])
