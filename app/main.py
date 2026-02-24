from agent import SimpleAgent


def main() -> None:
    agent = SimpleAgent()
    print("Framework Gemini Agent 已启动。输入 q 退出，输入 /clear 清空历史。")

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            print("已退出。")
            break
        if user_input == "/clear":
            agent.clear_history()
            print("历史已清空。")
            continue

        reply = agent.run(user_input)
        print(f"Agent: {reply}")


if __name__ == "__main__":
    main()
