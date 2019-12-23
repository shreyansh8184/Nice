import asyncio
import subprocess
import logging
from nicegrill import utils
from telethon.errors.rpcerrorlist import MessageTooLongError

TERMLIST = {}

class Terminal:

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)


    async def termxxx(message):
        output = "\n\n"
        cmd = utils.get_arg(message)
        process = subprocess.Popen(
            cmd.split(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        template = (
            "\n<b>⬤ Input:</b>\n\n<i>{}</i>\n\n<b>⬤ Output:</b>\n<code>"
            .format(cmd))
        await message.edit(template)
        if process.poll() is not None:
            returncode = process.wait()
            result = template + "<i>{}</i>".format(
                "Process returned with exit code: " + str(returncode) if not process.stdout.read().decode()
                else process.stdout.read().decode())
            await message.edit(result)
            return
        TERMLIST.update({message.id: process})
        out = ""
        for line in process.stdout:
            out += "<i>{}\n</i>".format(line.decode() if line.decode else process.stderr.readline().decode())
            if len(out) < 4000 and message.id in TERMLIST:
                await message.edit(template + out)
            else:
                out = out[1000: -1]
                await message.edit(template + out)
            await asyncio.sleep(1)
        del TERMLIST[message.id]

    async def killxxx(message):
        if not message.is_reply:
            await message.edit("<i>You have to reply to a message with a process</i>")
            return
        process = await message.get_reply_message()
        if process.id not in TERMLIST:
            await message.edit("<i>No process running in that message</i>")
        else:
            TERMLIST[process.id].kill()
            del TERMLIST[process.id]
            await message.edit("<i>Successfully killed</i>")
