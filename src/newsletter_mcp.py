from fastmcp import FastMCP
# from fastmcp.apps.form import FormInput

from src.modules.subscribers import service as subscriber_service
from src.modules.subscribers.schema import SubscriberCreate

# susbription_form = FormInput(
#         model = SubscriberCreate,
#         name = "Create Subscriber Form",
#         title = "Add a susbcriber",
#         tool_name = "add_subscriber",
#         on_submit = subscriber_service.add,
#         send_message = True, 
#         submit_text = "Add Subscriber"
#         )


# Create a server instance with a descriptive name
mcp = FastMCP(name="Shyam's Newsletter Server")
# mcp.add_provider(susbription_form)

@mcp.tool(name="list_subscribers", description="a list of names and email of all the people who have subscribed to my newsletter")
def list_subscribers():
    '''a list of names and email of all the people who have subscribed to my newsletter'''


    subs = subscriber_service.list_all()
    ret  = subs if subs else {}
    return ret

@mcp.tool(name="subscribers_add", description="Add a subscriber by EMAIL.")
def subscribers_add(email: str, name: str):
    """Add a subscriber by EMAIL."""
    subscriber_service.add(SubscriberCreate(email=email, name=name))
 

if __name__ == "__main__":
    mcp.run()