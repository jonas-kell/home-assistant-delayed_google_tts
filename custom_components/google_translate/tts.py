"""Support for the Google speech service."""
from io import BytesIO
from pydub import AudioSegment
import logging

from gtts import gTTS, gTTSError
import voluptuous as vol

from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider

_LOGGER = logging.getLogger(__name__)

SUPPORT_LANGUAGES = [
    "af",
    "ar",
    "bg",
    "bn",
    "bs",
    "ca",
    "cs",
    "cy",
    "da",
    "de",
    "el",
    "en",
    "eo",
    "es",
    "et",
    "fi",
    "fr",
    "gu",
    "hi",
    "hr",
    "hu",
    "hy",
    "id",
    "is",
    "it",
    "iw",
    "ja",
    "jw",
    "km",
    "kn",
    "ko",
    "la",
    "lv",
    "mk",
    "ml",
    "mr",
    "my",
    "ne",
    "nl",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "si",
    "sk",
    "sq",
    "sr",
    "su",
    "sv",
    "sw",
    "ta",
    "te",
    "th",
    "tl",
    "tr",
    "uk",
    "ur",
    "vi",
    # dialects
    "zh-CN",
    "zh-cn",
    "zh-tw",
    "en-us",
    "en-ca",
    "en-uk",
    "en-gb",
    "en-au",
    "en-gh",
    "en-in",
    "en-ie",
    "en-nz",
    "en-ng",
    "en-ph",
    "en-za",
    "en-tz",
    "fr-ca",
    "fr-fr",
    "pt-br",
    "pt-pt",
    "es-es",
    "es-us",
]

CONF_DELAY = "delay"

DEFAULT_LANG = "en"
DEFAULT_DELAY = 0

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORT_LANGUAGES),
        vol.Optional(CONF_DELAY, default=DEFAULT_DELAY): vol.All(int, vol.Range(min=0, max=15000)),
    }
)


async def async_get_engine(hass, config, discovery_info=None):
    """Set up Google speech component."""
    return GoogleProvider(hass, config)


class GoogleProvider(Provider):
    """The Google speech API provider."""

    def __init__(self, hass, conf):
        """Init Google TTS service."""
        self.hass = hass
        self._lang = conf[CONF_LANG]
        self._delay = conf[CONF_DELAY]
        self.name = "Google (custom)"

    @property
    def default_language(self):
        """Return the default language."""
        return self._lang

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    def get_tts_audio(self, message, language, options=None):
        """Load TTS from google."""
        tts = gTTS(text=message, lang=language)
        mp3_data = BytesIO()

        try:
            tts.write_to_fp(mp3_data)
        except gTTSError as exc:
            _LOGGER.exception("Error during processing of TTS request %s", exc)
            return None, None

        if self._delay != 0:
            as_tts = AudioSegment.from_file(BytesIO(mp3_data.getvalue()), "mp3")
            as_sil = AudioSegment.silent(duration=self._delay, frame_rate=as_tts.frame_rate)
            as_out = as_sil + as_tts + as_sil
            output=BytesIO()
            as_out.export(output, format="wav")
            return ("wav", output.getvalue())
        else:
            return "mp3", mp3_data.getvalue()


