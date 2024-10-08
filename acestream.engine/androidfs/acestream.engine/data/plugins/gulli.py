#-plugin-sig:ADn7EAHiGIl3fpRcy9M2NcodElifhTr2dUlfyNkO2m3Lx6kEQfxzd+Pca9F4y72SsnAFCfpBxdpFrBlU+aK4/snT/st17r/Ytfx2egRal2mWGkpfCjed7wahob/g3IK1GrE3F0hKCn/+lOtHyp1GRkA9OwK50hFqndm/ctgIab3mh+IGmrAiJbwXZXJ4x0b2GLyTPAyj0lBSm7zgrW+OQKC3Fo3N//PuYkFAUXgTruKEiFrPrjYrd/ExgwaIBKRH50OeHK4mlnPgmoMtBrkKhiqxIAcnaBj8M/rrUnatxzQPHXjka6oR0yY8yuTjXqQlnp2rjjBSPPseYQi4yyiRGg==
"""
$description French live TV channel and video on-demand service owned by Gulli.
$url replay.gulli.fr
$type live, vod
$region France
"""

import logging
import re

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream
from streamlink.stream.http import HTTPStream


log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://replay\.gulli\.fr/(?:Direct|.+/(?P<video_id>VOD\d+))",
))
class Gulli(Plugin):
    LIVE_PLAYER_URL = "https://replay.gulli.fr/jwplayer/embedstreamtv"
    VOD_PLAYER_URL = "https://replay.gulli.fr/jwplayer/embed/{0}"

    _playlist_re = re.compile(r"sources: (\[.+?\])", re.DOTALL)
    _vod_video_index_re = re.compile(r"jwplayer\(idplayer\).playlistItem\((?P<video_index>[0-9]+)\)")
    _mp4_bitrate_re = re.compile(r".*_(?P<bitrate>[0-9]+)\.mp4")

    _video_schema = validate.Schema(
        validate.all(
            validate.transform(lambda x: re.sub(r'"?file"?:\s*[\'"](.+?)[\'"],?', r'"file": "\1"', x, flags=re.DOTALL)),
            validate.transform(lambda x: re.sub(r'"?\w+?"?:\s*function\b.*?(?<={).*(?=})', "", x, flags=re.DOTALL)),
            validate.parse_json(),
            [
                validate.Schema({
                    "file": validate.url(),
                }),
            ],
        ),
    )

    def _get_streams(self):
        video_id = self.match.group("video_id")
        if video_id is not None:
            # VOD
            live = False
            player_url = self.VOD_PLAYER_URL.format(video_id)
        else:
            # Live
            live = True
            player_url = self.LIVE_PLAYER_URL

        res = self.session.http.get(player_url)
        playlist = re.findall(self._playlist_re, res.text)
        index = 0
        if not live:
            # Get the index for the video on the playlist
            match = self._vod_video_index_re.search(res.text)
            if match is None:
                return
            index = int(match.group("video_index"))

        if not playlist:
            return
        videos = self._video_schema.validate(playlist[index])

        for video in videos:
            video_url = video["file"]

            # Ignore non-supported MSS streams
            if "isml/Manifest" in video_url:
                continue

            try:
                if ".m3u8" in video_url:
                    yield from HLSStream.parse_variant_playlist(self.session, video_url).items()
                elif ".mp4" in video_url:
                    match = self._mp4_bitrate_re.match(video_url)
                    bitrate = "vod" if match is None else f"{match.group('bitrate')}k"
                    yield bitrate, HTTPStream(self.session, video_url)
            except OSError as err:
                if "403 Client Error" in str(err):
                    log.error("Failed to access stream, may be due to geo-restriction")
                raise


__plugin__ = Gulli
