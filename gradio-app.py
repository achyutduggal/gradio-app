import gradio as gr
import requests
import uvicorn
from fastapi import FastAPI
from openai import OpenAI
import os
import io
import base64
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------- API URLs ------------------------- #
API_URL = "https://listing-be-ihy4.onrender.com/update-listing/1"
API_URL_2 = "https://listing-be-ihy4.onrender.com/update-listing/2"

# ------------------------- OpenAI Client Setup ------------------------- #
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# ------------------------- Listing Update Functions ------------------------- #
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


# ------------------------- Image Description Function ------------------------- #
def generate_image_description(image):
    """
    Generate a detailed description of the uploaded image.
    """
    print("Starting image description generation...")

    if image is None:
        print("No image provided for description")
        return "Please upload an image to generate a description."

    try:
        print(f"Processing image of size: {image.size}")
        # Convert the PIL Image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        print("Image successfully converted to base64")

        # Prompt for image description
        image_prompt = """Act as an Image Description Generator. Please provide a detailed, accurate, and professional description of the image uploaded by the user. 
        Take into account all visible elements, their arrangement, colors, context, and any potential symbolism or significant details that might not be immediately apparent. 
        Additionally, consider any cultural, historical, or artistic references that may be relevant to interpreting the image. 
        If possible, please also provide insight into the mood, tone, or atmosphere conveyed by the image. 
        Your description should aim to be comprehensive and tailored to the specific content of the image, ensuring a unique and high-quality response for each user input."""

        print("Sending image to OpenAI for analysis...")
        # Call the OpenAI/ChatGPT-like client to analyze the image
        image_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an excellent observer and helpful assistant."},
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
        print(f"Image description generated successfully: {len(image_description)} characters")
        return image_description

    except Exception as e:
        print(f"ERROR in image description: {str(e)}")
        return f"Error analyzing image: {str(e)}"


# ------------------------- Instagram Caption Function ------------------------- #
def generate_instagram_caption(image_description, target_audience, interest_desire_goals,
                               post_content, tone_style, post_reason, call_to_action):
    """
    Generate Instagram captions based on the provided parameters and optional image description.
    The post_content parameter may be the image description itself.
    """
    print("Starting Instagram caption generation...")
    print(f"Using post_content: {post_content[:100]}..." if len(
        post_content) > 100 else f"Using post_content: {post_content}")

    try:
        # Prepare the prompt
        prompt = f"""
        Create an engaging and witty Instagram caption targeting {target_audience} who are interested in {interest_desire_goals}.
        The 200 word post should {post_content}, while incorporating {tone_style} to grab the reader's attention.
        The main message should be {post_reason}.
        Finally, the caption should end with a call to action to {call_to_action}.

        Tips for Crafting Your Caption:
        Identify Your Target Audience:

        Clearly define who you're speaking to (age, interests, demographics).
        Focus on Their Interests or Goals:

        Understand what your audience cares about. Is it fitness, travel, fashion? Tailor your message to resonate with their desires.
        Set the Post's Purpose:

        Determine what you want to convey. Is it to inspire, inform, entertain, or promote something?
        Choose Your Tone and Style:

        Decide on a voice that matches your brand. Do you want to be witty, playful, inspirational, or relatable?
        Address Any Objections:

        Think about what might hold your audience back. Address concerns or misconceptions directly in a lighthearted way.
        Craft a Strong Call to Action:

        Encourage engagement by telling your audience exactly what you want them to do next (like, comment, share,
        """

        print("Sending caption request to OpenAI...")
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
        print(f"Caption generated successfully: {len(caption)} characters")
        return caption

    except Exception as e:
        print(f"ERROR in caption generation: {str(e)}")
        return f"Error generating caption: {str(e)}"


# ------------------------- Combined Caption Generation Function ------------------------- #
def generate_complete_caption(image, target_audience, interest_desire_goals,
                              original_post_content, tone_style, post_reason, call_to_action):
    print("\n===== STARTING COMPLETE CAPTION PROCESS =====")
    # First generate image description if image is provided
    if image is not None:
        print(f"Image provided: {type(image)}, generating description first...")
        image_description = generate_image_description(image)
        print("Using generated image description for post_content")
        # Use image description as post content
        actual_post_content = image_description
    else:
        print("No image provided, using original post_content")
        image_description = ""
        actual_post_content = original_post_content

    print(f"Target audience: {target_audience}")
    print(f"Interests: {interest_desire_goals}")
    print(f"Tone: {tone_style}")
    print(f"Post reason: {post_reason}")
    print(f"Call to action: {call_to_action}")

    # Then generate caption with appropriate content
    result = generate_instagram_caption(image_description, target_audience, interest_desire_goals,
                                        actual_post_content, tone_style, post_reason, call_to_action)
    print("===== CAPTION GENERATION COMPLETE =====\n")
    return result


# ------------------------- Generate and Update Function ------------------------- #
def generate_and_update(image, target_audience, interest_desire_goals,
                        original_post_content, tone_style, post_reason, call_to_action):
    result = generate_complete_caption(image, target_audience, interest_desire_goals,
                                       original_post_content, tone_style, post_reason, call_to_action)

    # If image was provided, also return the updated description
    if image is not None:
        description = generate_image_description(image)
        return result, description
    return result, None


# ------------------------- Gradio App ------------------------- #
app = FastAPI()


@app.get("/")
def get_gradio():
    return {"message": "This is your main app"}


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

        # ----------- Tab 2: Instagram Caption Generator with Separate Functions ----------- #
        with gr.Tab("Instagram Caption Generator"):
            gr.Markdown(
                "Upload an image to analyze it, then use that description to generate a tailored Instagram caption.")

            # Image upload section
            with gr.Row():
                image_input = gr.Image(label="Upload Image", type="pil")

            # Image description section
            with gr.Row():
                analyze_image_btn = gr.Button("Analyze Image")
                image_description_output = gr.Textbox(label="Image Analysis", lines=6)

            # Caption parameters section
            with gr.Row():
                with gr.Column():
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
                        lines=2
                    )
                with gr.Column():
                    tone_style = gr.Textbox(
                        label="Tone & Style",
                        value="inspirational and encouraging",
                        lines=2
                    )
                    post_reason = gr.Textbox(
                        label="Reason for Post (Objection to Address)",
                        value="show that luxury can be accessible",
                        lines=2
                    )
                    call_to_action = gr.Textbox(
                        label="Call to Action",
                        value="book a tour",
                        lines=2
                    )

            # Caption generation section
            with gr.Row():
                generate_caption_btn = gr.Button("Generate Caption")
                caption_output = gr.Textbox(label="Generated Caption", lines=10)

            # Connect buttons to functions
            analyze_image_btn.click(
                fn=generate_image_description,
                inputs=[image_input],
                outputs=[image_description_output]
            )

            # Button for complete caption process
            generate_caption_btn.click(
                fn=generate_and_update,
                inputs=[
                    image_input,  # Use image directly instead of description
                    target_audience,
                    interest_desire_goals,
                    post_content,  # This will be used as fallback if no image
                    tone_style,
                    post_reason,
                    call_to_action
                ],
                outputs=[caption_output, image_description_output]
            )

# Launch the application
# demo.launch()
app = gr.mount_gradio_app(app, demo, path='/gradio')
