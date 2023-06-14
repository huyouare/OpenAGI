"""
tools/phone_call.py

A tool that allows the agent to make a phone call.

"""

from core.tool import BaseTool, InputSpec, OutputSpec
import os
import vocode
from vocode.streaming.telephony.hosted.outbound_call import OutboundCall
from vocode.streaming.models.telephony import CallEntity
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.telephony import TwilioConfig


class PhoneCall(BaseTool):
    def __init__(self):
        vocode.api_key = os.getenv("VOCODE_API_KEY")
        self.phone_number: str = os.getenv("RECIPIENT_PHONE_NUMBER")
        self.prompt: str = None
        self.caller_phone_number: str = os.getenv("CALLER_PHONE_NUMBER")

    def description(self) -> str:
        return "Makes a phone call."

    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("phone_number", "The phone number to call", "string"),
            InputSpec("prompt", "A comprehensive LLM prompt including context given to the LLM agent making the phone cal. The prompt should start with 'You are...'", "string"),
        ]

    def output_spec(self) -> list[OutputSpec]:
        return []

    def parse_input(self, input_str: str):
        self.phone_number = input_str["phone_number"]
        self.prompt = input_str["prompt"]

    def run(self):
        call = OutboundCall(
            recipient=CallEntity(
                phone_number=self.phone_number,
            ),
            caller=CallEntity(
                phone_number=self.caller_phone_number,
            ),
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello!"),
                prompt_preamble=self.prompt,
            ),
            twilio_config=TwilioConfig(
                account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
                auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
            )
        )
        call.start()

        return {
                "output": f"Calling {self.phone_number} with prompt {self.prompt}",
            }


if __name__ == "__main__":
    tool = PhoneCall()
    tool.prompt = "You are a person named Jesse. You are calling Avis to request a refund for etoll charge for rental agreement number 12345, date of rental 4/20/23, and contact information blahblah@gmail.com and phone number 9995556666."
    tool.run()
