import asyncio
import websockets


async def chat_client(chat_name):
    uri = f"ws://localhost:8000/chat/{chat_name}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to : {chat_name}")


        message_queue = asyncio.Queue()


        async def receive_messages():
            while True:
                message = await websocket.recv()
                await message_queue.put(message)


        async def send_messages():
            while True:
                message = await asyncio.to_thread(input, "Enter message: ")
                await websocket.send(message)


        async def display_messages():
            while True:
                message = await message_queue.get()
                print(f"\n{message}")
                message_queue.task_done()


        receive_task = asyncio.create_task(receive_messages())
        send_task = asyncio.create_task(send_messages())
        display_task = asyncio.create_task(display_messages())

        await asyncio.gather(receive_task, send_task, display_task)

if __name__ == "__main__":
    chat_name = input("Enter chat name: ")
    asyncio.run(chat_client(chat_name)  )