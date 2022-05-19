import asyncio

from brownie import Contract, network


class WebIIIService:
    @staticmethod
    def init_crt(address: str):
        token_crt = Contract(address)
        return token_crt

    @staticmethod
    def handle_event(event):
        print(event)

    @staticmethod
    async def log_loop(event_filter, poll_interval):
        while True:
            for PairCreated in event_filter.get_new_entries():
                WebIIIService.handle_event(PairCreated)
            await asyncio.sleep(poll_interval)


def main():
    print(network.is_connected())
    print(network.chain[17433372])
    contract = WebIIIService.init_crt("0xedf09d8423d150ee3f31a1b27da71bdae419ddaf")
    event_filter = contract.events.Swap.createFilter(fromBlock="latest")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(WebIIIService.log_loop(event_filter, 2)))
    finally:
        loop.close()


if __name__ == "__main__":
    main()
