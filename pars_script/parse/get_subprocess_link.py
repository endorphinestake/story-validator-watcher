def get_command(tokens):
    command = [
        "cosmos-validator-watcher",
        "--node", "https://story-testnet-rpc.blockhub.id:443"
    ]
    for token in tokens:
        command.append("--validator")
        command.append(f"{token['rpc']}:{token['moniker']}")
    return command
