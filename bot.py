from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import asyncio
import os
import random
import string

# Replace with your own values
api_id = '24490919'
api_hash = 'd1b3b15126c47dd4cb491553ee1db910'
owner_chat_id = '6876018655'
session_string = 'BAApYoLU0Klb25iA3fItWaIdsTfdGHupYys0v1Dd4AQiI75ktZOfp7AY314Z6vYUzhdffYapzbh_Mqo_RN5-UjHbyGl_yc0HdViFVxgHTOBf5JGF6yq8EX068ecrGuMBCnxN1MeqqWVnMA6AIskmkr_7myS4CB67t5FTjajDGYdAAh_usOYwy0wyqDMXRnWMnMrVZUBX1vF9g2Nijg0QvsHOfaFeWBuaDP9HeR68FgPt4Q5u_WnKbElza0vfey6AVq5_UtQDv-wzTeSWePnx_mE3OIWv4tK4iDjNrn5TSUSz_6_ur4jWU5YPn_ZOSbl322fBzt60E55P1THzglKSazQnAAAAAYSLfM0A'

# Initialize the Telethon client
app = Client('userbot', api_id=api_id, api_hash=api_hash, session_string=session_string)

# Load authorized users and courses from saved data
authorized_users = {}
courses = {}
forwarding_users = {}
user_pages = {}

data_file = 'bot_data.json'

if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)
        authorized_users = data.get('authorizedUsers', {})
        courses = data.get('courses', {})

# Function to save authorized users and courses data
def save_data():
    data = {'authorizedUsers': authorized_users, 'courses': courses}
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

# Function to generate a unique course code
def generate_course_code():
    # Generate a random 3-character code (e.g., ABC)
    return ''.join(random.choices(string.ascii_uppercase, k=3))

# Initialize the courses with codes
for course_name in courses:
    if 'code' not in courses[course_name]:
        courses[course_name]['code'] = generate_course_code()
        save_data()  

# Function to check if a user is authorized
def is_authorized(user_id):
    return str(user_id) in authorized_users

# Owner commands
@app.on_message(filters.regex(r'/auth (\d+)'))
async def auth_command(client, message):
    user_id = message.chat.id
    if str(user_id) == owner_chat_id:
        match = message.matches[0].group(1)
        authorized_users[match] = True
        save_data()
        await message.reply(f'User {match} is now authorized to use the bot.')
    else:
        await message.reply('Unauthorized owner.')

@app.on_message(filters.regex(r'/unauth (\d+)'))
async def unauth_command(client, message):
    user_id = message.chat.id
    if str(user_id) == owner_chat_id:
        match = message.matches[0].group(1)
        if match in authorized_users:
            del authorized_users[match]
            save_data()
            await message.reply(f'User {match} has been unauthorized from using the bot.')
        else:
            await message.reply(f'User {match} is not authorized.')
    else:
        await message.reply('Unauthorized owner.')

@app.on_message(filters.regex(r'/addcourse (.+)'))
async def add_course(client, message):
    user_id = message.chat.id
    if str(user_id) == owner_chat_id:
        course_info = message.matches[0].group(1).split(',')
        course_name = course_info[0].strip()
        start_message_id = int(course_info[1].strip())
        end_message_id = int(course_info[2].strip())
        courses[course_name] = {'startMessageId': start_message_id, 'endMessageId': end_message_id}
        save_data()
        await message.reply(f'Course "{course_name}" added.')

@app.on_message(filters.regex(r'/delcourse (.+)'))
async def del_course(client, message):
    user_id = message.chat.id
    if str(user_id) == owner_chat_id:
        course_name = message.matches[0].group(1).strip()
        if course_name in courses:
            del courses[course_name]
            save_data()
            await message.reply(f'Course "{course_name}" deleted.')
        else:
            await message.reply(f'Course "{course_name}" not found.')

@app.on_message(filters.regex(r'/broadcast (.+)'))
async def broadcast(client, message):
    user_id = message.chat.id
    if str(user_id) == owner_chat_id:
        broadcast_message = message.matches[0].group(1)
        for user_id in authorized_users:
            await client.send_message(user_id, broadcast_message)
        await message.reply('Broadcast sent.')
        
 # Handle the /total command to count all courses
@app.on_message(filters.regex(r'/total'))
async def total_courses_command(client, message):
    user_id = message.chat.id
    total_course_count = len(courses)

    if total_course_count == 0:
        await app.send_message(user_id, 'There are no courses available.')
    else:
        await app.send_message(user_id, f'Total number of courses available: {total_course_count}')       
        
# Handle the /cancel command to stop ongoing forwarding
@app.on_message(filters.regex(r'/cancel'))
async def cancel_forwarding(client, message):
    user_id = message.chat.id
    if str(user_id) in forwarding_users:
        del forwarding_users[str(user_id)]
        await app.send_message(user_id, 'Forwarding has been canceled.')
    else:
        await app.send_message(user_id, 'There is no ongoing forwarding to cancel.')
        

@app.on_message(filters.command("start"))
async def start_command(client, message):
    chat_id = message.chat.id

    welcome_message = (
        "🌟 **Advance hu mai ... ** 🤖📚\n\n"
       
    )

    await client.send_message(chat_id, text=welcome_message, disable_web_page_preview=True)

# Define a dictionary to store serial numbers for each course
course_serial_numbers = {}

# Function to initialize and update course serial numbers
def update_course_serial_numbers():
    course_names = list(courses.keys())
    total_courses = len(course_names)

    # Assign serial numbers to courses
    for i, course_name in enumerate(course_names, start=1):
        course_serial_numbers[course_name] = i

# Initialize course serial numbers
update_course_serial_numbers()

# Function to display the list of courses along with course codes and serial numbers
async def display_course_list(user_id, page_number):
    course_names = list(courses.keys())
    total_courses = len(course_names)

    start_idx = (page_number - 1) * 10
    end_idx = min(start_idx + 10, total_courses)
    page_course_names = course_names[start_idx:end_idx]

    response_text = f"📖✨ Choose a course by entering its number (C{start_idx + 1}-C{end_idx}):\n\n"
    for i, course_name in enumerate(page_course_names, start=start_idx + 1):
        course_code = courses[course_name]['code']
        serial_number = course_serial_numbers[course_name]
        response_text += f"{serial_number}. C{course_code}. {course_name}\n"

    if page_number > 1:
        response_text += "\nUse /p for the previous page."
    if page_number < (total_courses + 9) // 10:
        response_text += "\nUse /n for the next page."

    await app.send_message(user_id, response_text)

# Handle /getcourse command
@app.on_message(filters.regex(r'/getcourse'))
async def get_course_command(client, message):
    user_id = message.from_user.id

    if str(user_id) in forwarding_users:
        await app.send_message(user_id, 'You are currently forwarding messages. Use /cancel to stop forwarding.')
    elif not is_authorized(user_id):
        await app.send_message(user_id, 'You are not authorized to use the bot. Contact the owner for authorization.')
    else:
        user_pages[user_id] = 1  # Reset user's course page to the first page
        await display_course_list(user_id, page_number=1)

# Handle /p (previous page) command
@app.on_message(filters.regex(r'/p'))
async def previous_page_command(client, message):
    user_id = message.chat.id
    page_number = user_pages.get(user_id, 1)

    if page_number > 1:
        page_number -= 1
        user_pages[user_id] = page_number
        await display_course_list(user_id, page_number)

# Handle /n (next page) command
@app.on_message(filters.regex(r'/n'))
async def next_page_command(client, message):
    user_id = message.chat.id
    page_number = user_pages.get(user_id, 1)

    course_names = list(courses.keys())
    total_courses = len(course_names)

    if page_number < (total_courses + 9) // 10:
        page_number += 1
        user_pages[user_id] = page_number
        await display_course_list(user_id, page_number)

# Handle user input after selecting a course code
@app.on_message(filters.regex(r'^[A-Z]{3}$'))
async def course_code_input(client, message):
    user_id = message.chat.id
    user_input = message.text
    course_code = user_input  # Extract the course code

    # Find the course name associated with the code
    selected_course_name = None
    for course_name, course_info in courses.items():
        if 'code' in course_info and course_info['code'] == course_code:
            selected_course_name = course_name
            break

    if selected_course_name:
        if str(user_id) in forwarding_users:
            await app.send_message(user_id, 'You are currently forwarding messages. Use /cancel to stop forwarding.')
        else:
            course_info = courses[selected_course_name]
            total_messages = course_info['endMessageId'] - course_info['startMessageId'] + 1  # Calculate the total number of messages
            forwarding_users[str(user_id)] = {
                'courseName': selected_course_name,
                'awaitingSkipCount': True,  # Mark the user as awaiting skip count input
                'totalMessages': total_messages  # Store the total number of messages
            }
            await app.send_message(user_id, f'You have selected course: {selected_course_name}')
            await app.send_message(user_id, f'This course contains {total_messages} messages.')
            await app.send_message(user_id, f'How many messages would you like to skip for the "{selected_course_name}" course?')
    else:
        await app.send_message(user_id, 'Invalid course code. Please enter a valid course code.')


# Handle skip count input
@app.on_message(filters.regex(r'^\d+$'))
async def skip_count_input(client, message):
    user_id = message.chat.id
    user_input = int(message.text)
    if str(user_id) in forwarding_users and forwarding_users[str(user_id)]['awaitingSkipCount']:
        course_name = forwarding_users[str(user_id)]['courseName']

        if user_input >= 0:
            start_message_id = courses[course_name]['startMessageId'] + user_input
            end_message_id = courses[course_name]['endMessageId']
            forwarding_users[str(user_id)]['awaitingSkipCount'] = False  # User is no longer awaiting skip count
            await start_forwarding(client, user_id, course_name, user_input, start_message_id, end_message_id)  # Pass end_message_id
        else:
            await app.send_message(user_id, 'Please enter a non-negative number of messages to skip.')

async def start_forwarding(client, user_id, course_name, skip_count, start_message_id, end_message_id):
    delay_time = 0  # Adjust the delay time as needed (in seconds)
    channel_id = -1001902376170  # Replace with your channel ID

    if start_message_id > end_message_id:
        await client.send_message(user_id, 'You have reached the end of the course.')
        return

    forwarding_users[str(user_id)] = {'courseName': course_name, 'skipCount': skip_count, 'messageId': start_message_id, 'timeout': None}

    async def forwarding_loop():
        nonlocal start_message_id  # Declare start_message_id as nonlocal to modify it in the inner function
        if str(user_id) in forwarding_users:
            try:
                original_message = await client.get_messages(channel_id, start_message_id)
                await client.send_message(user_id, original_message.text, reply_markup=original_message.reply_markup)
                print(f'Forwarded message {start_message_id} to user {user_id}')
                start_message_id += 1

                if start_message_id <= end_message_id:
                    forwarding_users[str(user_id)]['timeout'] = await asyncio.sleep(delay_time)
                    await forwarding_loop()  # Continue forwarding after the delay
                else:
                    del forwarding_users[str(user_id)]
                    await client.send_message(user_id, f'Forwarded messages for {course_name}')
            except Exception as e:
                print(f'Error forwarding message {start_message_id}: {str(e)}')

    await forwarding_loop()


    
    
if __name__ == "__main__":
    print("Hello, World!")
app.run()
