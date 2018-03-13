
# Wrappers used for gamestate and scorekeeper

def admin_check(f):
    def wrapped_command(self):
        channel = self.args["channel"]

        if self.gamestate.state[channel]["admins"] and self.args["user"] not in self.gamestate.state[channel]["admins"]:
            yield (None, "Sorry <@{user}> but you need to be a game admin to do that :upside_down_face:".format(**self.args))

            admins = ["<@{0}>".format(admin) for admin in self.gamestate.state[channel]["admins"]]
            yield (None, "Game admins currently are: {0}".format(", ".join(admins)))
            raise StopIteration

        for channel, response in f(self):
            yield channel, response

    return wrapped_command

def only_in_progress(f):
    def wrapped_command(self):
        channel = self.args["channel"]

        if not self.gamestate.in_progress(channel):
            yield (None, "Sorry but we need the game to be in progress first! Get someone to kick it off!")
            raise StopIteration

        for channel, response in f(self):
            yield channel, response

    return wrapped_command
