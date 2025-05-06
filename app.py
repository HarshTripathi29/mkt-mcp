import os
import asyncio
import traceback
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import AzureChatOpenAI
from mcp.client.sse import sse_client
from mcp import ClientSession
from langgraph.prebuilt import create_react_agent

# Set Azure OpenAI environment variables
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://genaipocllmopenai.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "86b4802d401d4716ac7b1da620c77b14"

# Initialize the model
model = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    api_version="2024-02-01",
)

# Async conversion function using SSE
async def run_conversion(file_path: str):
    try:
        print(f"Converting PDF: {file_path}")
        # Connect to MCP SSE server (you can specify the URL directly if needed)
        async with sse_client("http://127.0.0.1:3001/markitdown-mcp") as (read, write):
            print("✅ Connected to MCP SSE server.")

            async with ClientSession(read, write) as session:
                print("🔁 Initializing session...")
                await session.initialize()

                # Load MCP tools
                print("🔧 Loading tools...")
                tools = await load_mcp_tools(session)
                print(f"🛠️ Tools loaded: {tools}")

                # Create REACT agent
                print("🧠 Creating REACT agent...")
                agent = create_react_agent(model, tools)
                print("✅ Agent ready.")

                # Provide file path for conversion
                print(f"📂 Reading file: {file_path}")
                result = await agent.ainvoke({
                    "messages": [{
                        "role": "user",
                        "content": f"Convert the following file to markdown:\n\n{file_path}"
                    }]
                })
                print("✅ Conversion completed.")
                return result["messages"][-1].content

    except Exception as e:
        print("\n❌ An error occurred during conversion:")
        print(e)
        traceback.print_exc()
        return None

# Main entry point
if __name__ == "__main__":
    input_path = r"C:\Users\harsh\Desktop\python\mcp\markitdown\Java_Interface_CheatSheet.pdf"
    output_path = "output_markdown.md"

    print(f"🚀 Starting conversion of {input_path}")
    result = asyncio.run(run_conversion(input_path))

    if result:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✅ Markdown saved to '{output_path}'")
        print("\n📄 Markdown Conversion Result:\n")
        print(result)
    else:
        print("❌ Conversion failed.")
