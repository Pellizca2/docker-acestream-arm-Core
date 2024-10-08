#-plugin-sig:Oek4fKjRVP6ORmE82zeCKv2RnyfAuSbMfxGlN95xIH19oJgZEKNEAl3XeNDkmLpScf5pDOebVV7zFviV5IFKrgBXJ1EtpL6JTV9lDZ1EgD/pYYMAg9xT0+jeTFv0nKs2BdeGfZoWUbMF9y3lsCBGIye7wmlK871vPE4zhGHEHGhpwdbqNQyvOjwjgF+TIZDKOwd6EsVJnX76IRxr2no/tMuawOFXzy0LtXQayEL2bFpvoqYf18YEKX/zU5ukVz+AK0aiEQt2TR2Y5j+KqY1aFywr9GM7TJ1cReY7PxtbuV9IY43+VB4Ef0oMgqp1yQ4au92f5K5ooAjCCrsPdJn7jw==
"""
$description German sports magazine live stream, owned by ARD.
$url sportschau.de
$type live
"""

import logging
import re

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream
from streamlink.stream.http import HTTPStream
from streamlink.utils.url import update_scheme


log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://(?:\w+\.)*sportschau\.de/",
))
class Sportschau(Plugin):
    def _get_streams(self):
        player_js = self.session.http.get(self.url, schema=validate.Schema(
            re.compile(r"https?:(//deviceids-medp.wdr.de/ondemand/\S+\.js)"),
            validate.none_or_all(
                validate.get(1),
                validate.transform(lambda url: update_scheme("https://", url)),
            ),
        ))
        if not player_js:
            return

        log.debug(f"Found player js {player_js}")
        data = self.session.http.get(player_js, schema=validate.Schema(
            validate.regex(re.compile(r"\$mediaObject\.jsonpHelper\.storeAndPlay\(({.+})\);?")),
            validate.get(1),
            validate.parse_json(),
            validate.get("mediaResource"),
            validate.get("dflt"),
            {
                validate.optional("audioURL"): validate.url(),
                validate.optional("videoURL"): validate.url(),
            },
        ))

        if data.get("videoURL"):
            yield from HLSStream.parse_variant_playlist(self.session, update_scheme("https:", data.get("videoURL"))).items()
        if data.get("audioURL"):
            yield "audio", HTTPStream(self.session, update_scheme("https:", data.get("audioURL")))


__plugin__ = Sportschau
