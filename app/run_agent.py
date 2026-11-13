
import argparse

from langchain_core.messages import AIMessage, ToolMessage
from app.agent import build_agent, AuthContext


DEMO_TOKENS = {
    "alice": "alice-demo-token",
    "bob": "bob-demo-token",
    "admin": "admin-demo-token"
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user",
        choices=DEMO_TOKENS.keys(),
        default="alice"
    )
    parser.add_argument(
        "--message",
        default="Show me promotion P-101 and its status."
    )
    parser.add_argument(
        "--confirm-approval",
        metavar="PROMOTION_ID",
        default=None,
        help="Request an explicit human confirmation for one promotion"
    )
    args = parser.parse_args()
    confirmed_id = None

    if args.confirm_approval:
        expected = f"APPROVE {args.confirm_approval}"

        answer = input(
            f"To authorize approval of {args.confirm_approval}, "
            f"type '{expected}': "
        )

        if answer.strip() == expected:
            confirmed_id = args.confirm_approval
        else:
            print("Confirmation not granted. Approval remains blocked.")

    agent = build_agent()

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": args.message}
            ]
        },
        context=AuthContext(
            token=DEMO_TOKENS[args.user],
            approved_promotion_id=confirmed_id
        ),
        config={"recursion_limit": 10}
    )

    print(f"\nAuthenticated demo user: {args.user}")

    for message in result["messages"]:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                print(
                    f"\nTOOL CALL: {call['name']} "
                    f"{call['args']}"
                )

        elif isinstance(message, ToolMessage):
            print(f"TOOL RESULT: {message.content}")

    print("\nAGENT RESPONSE:")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
