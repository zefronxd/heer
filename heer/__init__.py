from heer.core.bot import heer
from heer.core.dir import dirr
from heer.core.git import git
from heer.core.userbot import Userbot
from heer.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = heer()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
