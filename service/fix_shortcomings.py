from pyrogram import utils


class Fix:
    def __init__(self):
        utils.get_peer_type = self.get_peer_type_new

    def get_peer_type_new(self, peer_id: int) -> str:
        peer_id_str = str(peer_id)
        if not peer_id_str.startswith("-"):
            return "user"
        elif peer_id_str.startswith("-100"):
            return "channel"
        else:
            return "chat"