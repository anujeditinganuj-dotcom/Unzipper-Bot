# ===================================================================== #
#                      Copyright (c) 2022 Itz-fork                      #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                  #
# See the GNU General Public License for more details.                  #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>   #
# ===================================================================== #

import logging
from pyromod import listen
from .client.caching import update_cache

# Logging stuff
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Update cache (populates STRINGS used by Buttons class definition)
update_cache()

# Buttons (must be created before UnzipperBot is imported, since
# pyro_client.py does `from unzipper import Buttons` at import time)
from .helpers_nexa.buttons import Unzipper_Buttons
Buttons = Unzipper_Buttons()
# Client
from .client import UnzipperBot
unzip_client = UnzipperBot()
