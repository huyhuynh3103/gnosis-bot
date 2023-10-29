from web3 import Web3
from dotenv import load_dotenv
import os
from web3.middleware import geth_poa_middleware
from gnosis.eth import EthereumClient
from gnosis.safe import Safe
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Load env
load_dotenv()
api_key = os.getenv("API_KEY")
rpc_url = os.getenv("TESTNET_URL")
private_key = os.getenv("PRIVATE_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")
# rpc_url = os.getenv("MAINNET_URL")

# constant
RPC_URL = rpc_url + "?apikey=" + api_key
SAFE_ADDRESS = "0x31B18347BADe159DBBa6D4de92247947233BC060"  # testnet
STAKING_PROXY = "0x9C245671791834daf3885533D24dce516B763B28"  # testnet
VALIDATOR = "0xAcf8Bf98D1632e602d0B1761771049aF21dd6597"  # testnet
STAKING_ABI = '[{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"}],"name":"delegate","outputs":[],"stateMutability":"payable","type":"function"}]'
OPERATION_CALL = 0
OPERATION_DELEGATE_CALL = 1

# Create the web3 and contract instance
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
ethereum_client = EthereumClient(RPC_URL)
safe = Safe(SAFE_ADDRESS, ethereum_client)
staking_proxy = w3.eth.contract(address=STAKING_PROXY, abi=STAKING_ABI)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        interval = float(context.args[0])
        if interval < 0:
            await update.effective_message.reply_text("Sorry we can't set negative interval")
            return
        # context.job_queue.
        context.job_queue.run_repeating(callback=call_staking, interval=interval, chat_id=chat_id, name=str(chat_id))

        text = "Interval successfully set!"
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Bot successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


async def call_staking(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job

    """Call staking"""
    safe_info = safe.retrieve_all_info()
    print("safe_info: ", safe_info)
    data = staking_proxy.encodeABI(fn_name='delegate', args=[VALIDATOR])
    print("delegate info: ", data)
    gas = safe.estimate_tx_gas(to=STAKING_PROXY, value=1, data=data, operation=OPERATION_DELEGATE_CALL)
    print("estimate gas: ", gas)
    safe_tx = safe.build_multisig_tx(to=STAKING_PROXY, value=1, data=data, safe_tx_gas=gas)
    print("safe_tx: ", safe_tx)
    # owner 1 sign
    safe_tx.sign(private_key)
    is_success = safe_tx.call() == 1
    print("check safe_tx ok: ", is_success)
    print(w3.eth.get_block('latest'))
    (tx_hash, tx) = safe_tx.execute(private_key)
    print("tx", tx);
    await context.bot.send_message(job.chat_id, text=f"TxHash: {tx_hash}")


def main():
    # Create the telegram bot application
    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("stop", stop))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
