import gradio as gr
import requests
from openai import OpenAI
import os
import io
import base64
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------- Your Existing Code for Updating Listing ------------------------- #

API_URL = "https://listing-be-ihy4.onrender.com/update-listing/1"
API_URL_2 = "https://listing-be-ihy4.onrender.com/update-listing/2"

# ------------------------- Instagram Caption Generator Helper Function ------------------------- #
# Make sure you have installed the openai library with: pip install openai

# Replace this with your actual OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)




def update_listing_1(location, highlight, beds, baths, sqft, phone, email, image_url):
    data = {
        "location": location,
        "highlight": highlight,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "phone": phone,
        "email": email,
        "imageUrl": image_url
    }
    # POST request to the endpoint
    response = requests.post(API_URL, json=data)
    # Return response text or JSON
    try:
        return response.json()
    except:
        return response.text

def update_listing_2(location, highlight, beds, baths, sqft, phone, email, image_url):
    data = {
        "location": location,
        "highlight": highlight,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "phone": phone,
        "email": email,
        "imageUrl": image_url
    }
    # POST request to the endpoint
    response = requests.post(API_URL_2, json=data)
    # Return response text or JSON
    try:
        return response.json()
    except:
        return response.text


# ------------------------- Generate Description Function ------------------------- #
def generate_description():
    return

# ------------------------- Generate Instagram Caption Function ------------------------- #
def generate_instagram_caption(image, target_audience, interest_desire_goals,
                               post_content, tone_style, post_reason, call_to_action):
    """
    Generate Instagram captions based on the provided parameters and image.
    """
    try:
        # Prepare the prompt
        prompt = f"""
        Create an engaging and witty Instagram caption targeting {target_audience} who are interested in {interest_desire_goals}.
        The 200 word post should {post_content}, while incorporating {tone_style} to grab the reader's attention.
        The main message should be {post_reason}.
        Finally, the caption should end with a call to action to {call_to_action}.

        Tips for Crafting Your Caption:
        Identify Your Target Audience:

        Clearly define who you’re speaking to (age, interests, demographics).
        Focus on Their Interests or Goals:

        Understand what your audience cares about. Is it fitness, travel, fashion? Tailor your message to resonate with their desires.
        Set the Post’s Purpose:

        Determine what you want to convey. Is it to inspire, inform, entertain, or promote something?
        Choose Your Tone and Style:

        Decide on a voice that matches your brand. Do you want to be witty, playful, inspirational, or relatable?
        Address Any Objections:

        Think about what might hold your audience back. Address concerns or misconceptions directly in a lighthearted way.
        Craft a Strong Call to Action:

        Encourage engagement by telling your audience exactly what you want them to do next (like, comment, share,
        """

        # If there's an image, analyze it first
        image_description = ""
        if image is not None:
            # Convert the PIL Image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Example prompt for image description
            image_prompt = """ Act as an Image Description Generator. Please provide a detailed, accurate, and professional description of the image uploaded by the user. 
            Take into account all visible elements, their arrangement, colors, context, and any potential symbolism or significant details that might not be immediately apparent. 
            Additionally, consider any cultural, historical, or artistic references that may be relevant to interpreting the image. 
            If possible, please also provide insight into the mood, tone, or atmosphere conveyed by the image. 
            Your description should aim to be comprehensive and tailored to the specific content of the image, ensuring a unique and high-quality response for each user input. """

            # Call the OpenAI/ChatGPT-like client to analyze the image
            image_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a excellent observer and helpful assistant."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": image_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }
                ]
            )

            image_description = image_completion.choices[0].message.content
            prompt += f"\n\nImage description to incorporate: {image_description}"

        # Generate caption
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are a professional social media manager who specializes in creating engaging Instagram captions."},
                {"role": "user", "content": prompt}
            ]
        )

        caption = completion.choices[0].message.content

        # Return both image description and generated caption (if image was provided)
        if image is not None:
            return f"**Image Analysis:**\n\n{image_description}\n\n**Generated Caption:**\n\n{caption}"
        else:
            return f"**Generated Caption:**\n\n{caption}"

    except Exception as e:
        return f"Error generating caption: {str(e)}"


# ------------------------- Gradio App ------------------------- #
with gr.Blocks() as demo:
    gr.Markdown("# Real Estate App")

    with gr.Tabs():
        # ----------- Tab 1: Update Listing ----------- #
        with gr.Tab("Brochure Generator"):
            gr.Markdown("Fill out the details below and click **Submit** to update the listing:")

            loc = gr.Textbox(value="Downtown", label="Location", lines=1)
            hl = gr.Textbox(value="CITY PARK", label="Highlight", lines=1)
            bd = gr.Textbox(value="2", label="Beds", lines=1)
            bt = gr.Textbox(value="2", label="Baths", lines=1)
            sf = gr.Textbox(value="1500", label="Square Footage (sqft)", lines=1)
            ph = gr.Textbox(value="+123 456 7890", label="Phone", lines=1)
            em = gr.Textbox(value="agent@example.com", label="Email", lines=1)
            img_url = gr.Textbox(
                value="https://t4.ftcdn.net/jpg/02/87/98/61/360_F_287986158_2Tz2w7QKcgmbpecZZzveGUdN9RNPB3c4.jpg",
                label="Image URL",
                lines=1
            )

            submit_btn = gr.Button("Submit for 1st design")
            submit_btn_2 = gr.Button("Submit for 2nd design")
            output = gr.Textbox(label="Response from Server", lines=4)

            submit_btn.click(
                fn=update_listing_1,
                inputs=[loc, hl, bd, bt, sf, ph, em, img_url],
                outputs=[output],
            )

            submit_btn_2.click(
                fn=update_listing_2,
                inputs=[loc, hl, bd, bt, sf, ph, em, img_url],
                outputs=[output],

            )

        # ----------- Tab 2: Instagram Caption Generator ----------- #
        with gr.Tab("Instagram Caption Generator"):
            gr.Markdown(
                "Use the fields below to generate a tailored Instagram caption. Uploading an image is optional.")

            image_input = gr.Image(label="Upload Image (Optional)", type="pil")

            # Using multiple lines to give more space
            target_audience = gr.Textbox(
                label="Target Audience",
                value="first-time homebuyers in their 30s",
                lines=2
            )
            interest_desire_goals = gr.Textbox(
                label="Interests/Desires/Goals",
                value="finding a dream home in a safe neighborhood",
                lines=2
            )
            post_content = gr.Textbox(
                label="What Should the Caption Highlight?",
                value="unique features and modern amenities",
                lines=3
            )
            tone_style = gr.Textbox(
                label="Tone & Style",
                value="inspirational and encouraging",
                lines=2
            )
            post_reason = gr.Textbox(
                label="Reason for Post (Objection to Address)",
                value="show that luxury can be accessible",
                lines=3
            )
            call_to_action = gr.Textbox(
                label="Call to Action",
                value="book a tour",
                lines=2
            )

            generate_caption_btn = gr.Button("Generate Caption")
            caption_output = gr.Textbox(label="Generated Caption", lines=12)

            generate_caption_btn.click(
                fn=generate_instagram_caption,
                inputs=[
                    image_input,
                    target_audience,
                    interest_desire_goals,
                    post_content,
                    tone_style,
                    post_reason,
                    call_to_action
                ],
                outputs=caption_output
            )

demo.launch()
