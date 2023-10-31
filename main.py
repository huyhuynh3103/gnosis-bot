from web3 import Web3
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict
import os
from web3.middleware import geth_poa_middleware
from gnosis.eth import EthereumClient
from gnosis.safe import Safe
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    PicklePersistence,
    ConversationHandler,
    MessageHandler,
    filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()
api_key = os.getenv("API_KEY")

private_key = os.getenv("PRIVATE_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")
mainnet_rpc_url = os.getenv("MAINNET_URL")
testnet_rpc_url = os.getenv("TESTNET_URL")

EXPLORER_HOST_MAINNET = "https://app.roninchain.com"
EXPLORER_HOST_TESTNET = "https://saigon-app.roninchain.com"
STAKING_PROXY_MAINNET = "0x545edb750eB8769C868429BE9586F5857A768758"  # mainnet
STAKING_PROXY_TESTNET = "0x9C245671791834daf3885533D24dce516B763B28"  # testnet

STAKING_ABI = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"admin","type":"address"}],"name":"ErrAdminOfAnyActivePoolForbidden","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"},{"internalType":"string","name":"extraInfo","type":"string"}],"name":"ErrCannotInitTransferRON","type":"error"},{"inputs":[],"name":"ErrCannotTransferRON","type":"error"},{"inputs":[{"internalType":"enum ContractType","name":"contractType","type":"uint8"}],"name":"ErrContractTypeNotFound","type":"error"},{"inputs":[{"internalType":"bytes4","name":"msgSig","type":"bytes4"}],"name":"ErrDuplicated","type":"error"},{"inputs":[{"internalType":"address","name":"poolAddr","type":"address"}],"name":"ErrInactivePool","type":"error"},{"inputs":[{"internalType":"bytes4","name":"msgSig","type":"bytes4"},{"internalType":"uint256","name":"currentBalance","type":"uint256"},{"internalType":"uint256","name":"sendAmount","type":"uint256"}],"name":"ErrInsufficientBalance","type":"error"},{"inputs":[],"name":"ErrInsufficientDelegatingAmount","type":"error"},{"inputs":[],"name":"ErrInsufficientStakingAmount","type":"error"},{"inputs":[],"name":"ErrInvalidArrays","type":"error"},{"inputs":[],"name":"ErrInvalidCommissionRate","type":"error"},{"inputs":[],"name":"ErrInvalidPoolShare","type":"error"},{"inputs":[],"name":"ErrOnlyPoolAdminAllowed","type":"error"},{"inputs":[],"name":"ErrPoolAdminForbidden","type":"error"},{"inputs":[{"internalType":"bytes4","name":"msgSig","type":"bytes4"}],"name":"ErrRecipientRevert","type":"error"},{"inputs":[],"name":"ErrStakingAmountLeft","type":"error"},{"inputs":[],"name":"ErrThreeInteractionAddrsNotEqual","type":"error"},{"inputs":[{"internalType":"bytes4","name":"msgSig","type":"bytes4"},{"internalType":"enum RoleAccess","name":"expectedRole","type":"uint8"}],"name":"ErrUnauthorized","type":"error"},{"inputs":[],"name":"ErrUndelegateTooEarly","type":"error"},{"inputs":[],"name":"ErrUndelegateZeroAmount","type":"error"},{"inputs":[{"internalType":"bytes4","name":"msgSig","type":"bytes4"},{"internalType":"enum ContractType","name":"expectedContractType","type":"uint8"},{"internalType":"address","name":"actual","type":"address"}],"name":"ErrUnexpectedInternalCall","type":"error"},{"inputs":[],"name":"ErrUnstakeTooEarly","type":"error"},{"inputs":[],"name":"ErrUnstakeZeroAmount","type":"error"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"ErrZeroCodeContract","type":"error"},{"inputs":[],"name":"ErrZeroValue","type":"error"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minRate","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"maxRate","type":"uint256"}],"name":"CommissionRateRangeUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"enum ContractType","name":"contractType","type":"uint8"},{"indexed":true,"internalType":"address","name":"addr","type":"address"}],"name":"ContractUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minSecs","type":"uint256"}],"name":"CooldownSecsToUndelegateUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"delegator","type":"address"},{"indexed":true,"internalType":"address","name":"consensuAddr","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Delegated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"threshold","type":"uint256"}],"name":"MinValidatorStakingAmountUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"validator","type":"address"},{"indexed":true,"internalType":"address","name":"admin","type":"address"}],"name":"PoolApproved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"period","type":"uint256"},{"indexed":true,"internalType":"address","name":"poolAddr","type":"address"},{"indexed":false,"internalType":"uint256","name":"shares","type":"uint256"}],"name":"PoolSharesUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address[]","name":"validator","type":"address[]"}],"name":"PoolsDeprecated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"period","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"poolAddrs","type":"address[]"}],"name":"PoolsUpdateConflicted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"period","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"poolAddrs","type":"address[]"},{"indexed":false,"internalType":"uint256[]","name":"rewards","type":"uint256[]"}],"name":"PoolsUpdateFailed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"period","type":"uint256"},{"indexed":false,"internalType":"address[]","name":"poolAddrs","type":"address[]"},{"indexed":false,"internalType":"uint256[]","name":"aRps","type":"uint256[]"},{"indexed":false,"internalType":"uint256[]","name":"shares","type":"uint256[]"}],"name":"PoolsUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"poolAddr","type":"address"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"RewardClaimed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"consensuAddr","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Staked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"validator","type":"address"},{"indexed":true,"internalType":"address","name":"recipient","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"contractBalance","type":"uint256"}],"name":"StakingAmountDeductFailed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"validator","type":"address"},{"indexed":true,"internalType":"address","name":"admin","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"contractBalance","type":"uint256"}],"name":"StakingAmountTransferFailed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"delegator","type":"address"},{"indexed":true,"internalType":"address","name":"consensuAddr","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Undelegated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"consensuAddr","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Unstaked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"poolAddr","type":"address"},{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"debited","type":"uint256"}],"name":"UserRewardUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"secs","type":"uint256"}],"name":"WaitingSecsToRevokeUpdated","type":"event"},{"stateMutability":"payable","type":"fallback"},{"inputs":[],"name":"DEFAULT_ADDITION_GAS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERIOD_DURATION","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_candidateAdmin","type":"address"},{"internalType":"address","name":"_consensusAddr","type":"address"},{"internalType":"address payable","name":"_treasuryAddr","type":"address"},{"internalType":"uint256","name":"_commissionRate","type":"uint256"}],"name":"applyValidatorCandidate","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_consensusAddrs","type":"address[]"},{"internalType":"uint256[]","name":"_amounts","type":"uint256[]"}],"name":"bulkUndelegate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_consensusAddrList","type":"address[]"}],"name":"claimRewards","outputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"cooldownSecsToUndelegate","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"}],"name":"delegate","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_consensusAddrList","type":"address[]"},{"internalType":"address","name":"_consensusAddrDst","type":"address"}],"name":"delegateRewards","outputs":[{"internalType":"uint256","name":"_amount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"execDeductStakingAmount","outputs":[{"internalType":"uint256","name":"_actualDeductingAmount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_pools","type":"address[]"},{"internalType":"uint256","name":"_newPeriod","type":"uint256"}],"name":"execDeprecatePools","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_consensusAddrs","type":"address[]"},{"internalType":"uint256[]","name":"_rewards","type":"uint256[]"},{"internalType":"uint256","name":"_period","type":"uint256"}],"name":"execRecordRewards","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"getCommissionRateRange","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"enum ContractType","name":"contractType","type":"uint8"}],"name":"getContract","outputs":[{"internalType":"address","name":"contract_","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_pools","type":"address[]"}],"name":"getManySelfStakings","outputs":[{"internalType":"uint256[]","name":"_selfStakings","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_poolAddrs","type":"address[]"},{"internalType":"address[]","name":"_userList","type":"address[]"}],"name":"getManyStakingAmounts","outputs":[{"internalType":"uint256[]","name":"_stakingAmounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"_poolList","type":"address[]"}],"name":"getManyStakingTotals","outputs":[{"internalType":"uint256[]","name":"_stakingAmounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_poolAdminAddr","type":"address"}],"name":"getPoolAddressOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_poolAddr","type":"address"}],"name":"getPoolDetail","outputs":[{"internalType":"address","name":"_admin","type":"address"},{"internalType":"uint256","name":"_stakingAmount","type":"uint256"},{"internalType":"uint256","name":"_stakingTotal","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_poolAddr","type":"address"},{"internalType":"address","name":"_user","type":"address"}],"name":"getReward","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"address[]","name":"_poolAddrList","type":"address[]"}],"name":"getRewards","outputs":[{"internalType":"uint256[]","name":"_rewards","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_poolAddr","type":"address"},{"internalType":"address","name":"_user","type":"address"}],"name":"getStakingAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_poolAddr","type":"address"}],"name":"getStakingTotal","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"__validatorContract","type":"address"},{"internalType":"uint256","name":"__minValidatorStakingAmount","type":"uint256"},{"internalType":"uint256","name":"__maxCommissionRate","type":"uint256"},{"internalType":"uint256","name":"__cooldownSecsToUndelegate","type":"uint256"},{"internalType":"uint256","name":"__waitingSecsToRevoke","type":"uint256"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"initializeV2","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_poolAdminAddr","type":"address"}],"name":"isAdminOfActivePool","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minValidatorStakingAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddrSrc","type":"address"},{"internalType":"address","name":"_consensusAddrDst","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"redelegate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"}],"name":"requestEmergencyExit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"}],"name":"requestRenounce","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"},{"internalType":"uint256","name":"_effectiveDaysOnwards","type":"uint256"},{"internalType":"uint256","name":"_commissionRate","type":"uint256"}],"name":"requestUpdateCommissionRate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_minRate","type":"uint256"},{"internalType":"uint256","name":"_maxRate","type":"uint256"}],"name":"setCommissionRateRange","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"enum ContractType","name":"contractType","type":"uint8"},{"internalType":"address","name":"addr","type":"address"}],"name":"setContract","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_cooldownSecs","type":"uint256"}],"name":"setCooldownSecsToUndelegate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_threshold","type":"uint256"}],"name":"setMinValidatorStakingAmount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_secs","type":"uint256"}],"name":"setWaitingSecsToRevoke","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"}],"name":"stake","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_candidateAdmin","type":"address"},{"internalType":"address","name":"_consensusAddr","type":"address"},{"internalType":"address payable","name":"_treasuryAddr","type":"address"},{"internalType":"uint256","name":"_commissionRate","type":"uint256"}],"name":"tmp_re_applyValidatorCandidate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"undelegate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"unstake","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"waitingSecsToRevoke","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]'
OPERATION_CALL = 0
OPERATION_DELEGATE_CALL = 1



# state definitions
SELECTING_NETWORK, ENTER_SAFE_WALLET, ENTER_VALIDATOR, ENTER_STAKING_AMOUNT = map(chr, range(4))
ENTER_STAKE_TIME, ENTER_UNSTAKE_TIME, SELECTING_INTERVAL_TYPE, ENTER_INTERVAL = map(chr, range(4, 8))

END = ConversationHandler.END


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi, I'm Gnosis Bot and I'm here to help you staking your RON."
    )
    chat_id = update.effective_message.chat_id
    interval_type = context.user_data.get("interval-type")
    stake_time = context.user_data.get("stake-time")
    time = datetime.strptime(stake_time, "%H:%M")

    if interval_type == "daily":
        context.job_queue.run_daily(callback=call_staking,time=time, chat_id=chat_id,
                                    name=str(chat_id), data=context.user_data)
    elif interval_type == "monthly":
        context.job_queue.run_monthly(callback=call_staking, when=time, chat_id=chat_id,
                                    name=str(chat_id),  data=context.user_data)
    elif interval_type == "custom":
        interval = context.user_data.get("interval")
        context.job_queue.run_repeating(callback=call_staking, interval=interval, chat_id=chat_id,
                                    name=str(chat_id),  data=context.user_data)
    text = f"Job {chat_id} started"
    await update.effective_message.reply_text(text)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text(
        "Use /start to start the job that automatically stake/unstake. \n"
        "Use /set_safe_info to set info for onchain transactions. \n"
        "Use /setting to set info of job schedule. \n"
        "Use /show_data to show all cached data. \n"
        "Use /stop to stop all jobs."
    )



async def setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    reply_keyboard = [["daily", "monthly", "yearly", "custom"]]
    await update.message.reply_text("Set the job interval type: ",
                                    reply_markup=ReplyKeyboardMarkup(
                                        reply_keyboard, one_time_keyboard=True
                                    ),
                                    )
    return SELECTING_INTERVAL_TYPE


async def save_interval_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    interval_type = update.message.text
    is_custom = interval_type == "custom"
    context.user_data["interval-type"] = interval_type
    if interval_type == "yearly":
        await update.effective_message.reply_text(f"Sorry this enter ${interval_type} does not support now.")
        return END
    logger.info("Interval type: %s", interval_type)
    await update.message.reply_text(f"Success adding interval type! Interval type: {interval_type}")
    if is_custom:
        await update.effective_message.reply_text("You must enter the interval number: ",
                                                  reply_markup=ReplyKeyboardRemove())
        return ENTER_INTERVAL
    await update.message.reply_text(
        "Now enter stake time of day [HH:MM]: ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ENTER_STAKE_TIME


async def save_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    interval = int(update.message.text)
    context.user_data["interval"] = interval
    logger.info("Interval time: %s", interval)
    await update.message.reply_text(
        f"Interval time: {interval}"
    )
    await update.message.reply_text(
        "Now enter stake time of day [HH:MM]: "
    )
    return ENTER_STAKE_TIME


async def save_staking_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    stake_time = update.message.text
    context.user_data["stake-time"] = stake_time
    logger.info("Stake time: %s", stake_time)
    await update.message.reply_text(
        f"Success adding stake time! Stake time: {stake_time}"
    )
    await update.message.reply_text(
        "Now enter un-stake time of day [HH:MM]: "
    )
    return ENTER_UNSTAKE_TIME


async def save_unstake_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    unstake_time = update.message.text
    context.user_data["unstake-time"] = unstake_time
    logger.info("Unstake time: %s", unstake_time)
    await update.message.reply_text(
        f"Success adding unstake time! Staking time: {unstake_time}"
    )
    await update.message.reply_text(
        "Done!"
    )
    return END


async def set_stake_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    reply_keyboard = [["ronin-mainnet", "ronin-testnet"]]
    await update.message.reply_text("Choose your network",
                                    reply_markup=ReplyKeyboardMarkup(
                                        reply_keyboard, one_time_keyboard=True
                                    ),
                                    )
    return SELECTING_NETWORK


async def save_network(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    network = update.message.text
    context.user_data["network"] = network
    logger.info("Network: %s", network)
    await update.message.reply_text(f"Success adding network! Network: {network}")

    await update.message.reply_text(
        "Now enter your safe address: ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ENTER_SAFE_WALLET


async def save_safe_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    safe_wallet = update.message.text
    context.user_data["safe-wallet"] = safe_wallet
    logger.info("Safe address: %s", safe_wallet)
    await update.message.reply_text(
        f"Success adding safe wallet! Safe wallet: {safe_wallet}"
    )
    await update.message.reply_text(
        "Now enter the validator addresses: "
    )
    return ENTER_VALIDATOR


async def save_validator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    validator = update.message.text
    context.user_data["validator"] = validator
    logger.info("Validator: %s", validator)
    await update.message.reply_text(
        f"Success adding validator! Validator wallet: {validator}"
    )
    await update.message.reply_text(
        "Now enter amount staking: "
    )
    return ENTER_STAKING_AMOUNT


async def save_staking_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    staking_amount = update.message.text
    context.user_data["staking-amount"] = int(staking_amount)
    logger.info("Staking amount: %s", staking_amount)
    await update.message.reply_text(
        f"Success adding staking amount! Staking amount: {staking_amount}"
    )
    await update.message.reply_text(
        "Done!!."
    )
    return END


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Bot successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


def get_tx_url(network: str, tx_hash: str) -> str:
    if network == "ronin-testnet":
        return f"{EXPLORER_HOST_TESTNET}/tx/{tx_hash}"
    else:
        return f"{EXPLORER_HOST_MAINNET}/tx/{tx_hash}"


async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the gathered info."""
    await update.message.reply_text(
        f"This is what you already told me: {facts_to_str(context.user_data)}"
    )


async def call_staking(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Call staking"""
    job = context.job
    print(job.data)
    safe_address = job.data["safe-wallet"]
    validator = job.data["validator"]
    network = job.data["network"]
    staking_amount = job.data["staking-amount"]
    if network == "ronin-testnet":
        staking_address = STAKING_PROXY_TESTNET
        rpc_url = f"{testnet_rpc_url}?apikey={api_key}"
    else:
        staking_address = STAKING_PROXY_MAINNET
        rpc_url = f"{mainnet_rpc_url}?apikey={api_key}"
    try:
        # Create the web3 and contract instance
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        ethereum_client = EthereumClient(rpc_url)
        staking_contract = w3.eth.contract(address=staking_address, abi=STAKING_ABI)
        safe = Safe(safe_address, ethereum_client)

        safe_info = safe.retrieve_all_info()
        logger.info("safe info: ", safe_info)
        data = staking_contract.encodeABI(fn_name='delegate', args=[validator])
        logger.info("delegate info: ", str(data))

        gas = safe.estimate_tx_gas(to=staking_address, value=staking_amount, data=data,
                                   operation=OPERATION_DELEGATE_CALL)
        logger.info("estimate gas: ", gas)
        safe_tx = safe.build_multisig_tx(to=staking_address, value=staking_amount, data=data, safe_tx_gas=gas)
        logger.info("safe_tx: ", safe_tx)
        # owner 1 sign
        safe_tx.sign(private_key)
        is_success = safe_tx.call() == 1
        logger.info("check safe_tx ok: ", is_success)
        logger.info(w3.eth.get_block('latest'))
        (tx_hash, tx) = safe_tx.execute(private_key)
        logger.info("tx", tx)
        await context.bot.send_message(job.chat_id, text=f"TxHash: {get_tx_url(network, tx_hash.hex())}")
    except Exception as error:
        # handle the exception
        logger.error("An exception occurred:", error)
        await context.bot.send_message(job.chat_id, text=f"Revert with {type(error).__name__}")


def main():
    # Create the telegram bot application
    persistence = PicklePersistence(filepath="gnosis")
    application = Application.builder().token(telegram_token).persistence(persistence).build()

    staking_handler = ConversationHandler(
        entry_points=[
            CommandHandler("set_stake_info", set_stake_info),
        ],
        states={
            SELECTING_NETWORK: [MessageHandler(filters.Regex("^(ronin-mainnet|ronin-testnet)$"), save_network)],
            ENTER_SAFE_WALLET: [MessageHandler(filters.Regex("^0x[a-fA-F0-9]{40}$"), save_safe_wallet)],
            ENTER_VALIDATOR: [MessageHandler(filters.Regex("^0x[a-fA-F0-9]{40}$"), save_validator)],
            ENTER_STAKING_AMOUNT: [MessageHandler(filters.Regex("^\d+$"), save_staking_amount)],
        },
        fallbacks=[
            CommandHandler("stop", stop)
        ],
        name="stake-info",
        persistent=True,
    )

    setting_handler = ConversationHandler(
        entry_points=[
            CommandHandler("setting", setting),
        ],
        states={
            SELECTING_INTERVAL_TYPE: [
                MessageHandler(filters.Regex("^(daily|monthly|yearly|custom)$"), save_interval_type)],
            ENTER_INTERVAL: [
                MessageHandler(filters.Regex("^\d+$"), save_interval)],
            ENTER_STAKE_TIME: [MessageHandler(filters.Regex("^([01]?[0-9]|2[0-3]):[0-5][0-9]"), save_staking_time)],
            ENTER_UNSTAKE_TIME: [MessageHandler(filters.Regex("^([01]?[0-9]|2[0-3]):[0-5][0-9]"), save_unstake_time)],
        },
        fallbacks=[
            CommandHandler("stop", stop)
        ],
        name="setting",
        persistent=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show_data", show_data))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(staking_handler)
    application.add_handler(setting_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
