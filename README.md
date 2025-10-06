<<<<<<< Updated upstream
# LLM Travel Assistant
## Description:
This product tends to help the users to travel to a location with ease with the help of AI. The users can enquire about traveling to a location, get travel insights like the ideal budget needed to visit the place, the popular tourist attractions situated there, the rules and regulations and queries with a chatbot. This helps the user to plan the trip accordingly to make it a memorable one. Not only does this product helps in the initial planning phase but can also do a lot more than that.
## Things done by the product:
### 1.	General Enquiry
Not all users have a particular location on their mind. Or some could have a few questions before confirming a spot for their vacation. Some would just want to go explore a new place but not sure where. This component helps all kinds of users get a clear picture of when and where to go. Users can for instance ask about:
a)	Is it safe to go to a hill station next month keeping in mind about the weather conditions?
b)	I want to go on a trip to some famous monuments in Spain as a group of 5 people. What would be the ideal budget and structure me a 5 day plan.
With the help of APIs and up-to date information, the AI chatbot would provide accurate and satisfactory results to the users.
### 2.	Trip Planning
Once a location has been finalized, the dates, budget, locations to visit are all discussed. This is when the itinerary list is created and modified according to the user’s preferences. The AI would suggest some modifications if required to the current list to make the trip a more valuable one. 
### 3.	Tickets Booking
After the planning phase is completed with the locations, budget, group and dates finalized, it is time to make travel arrangements. The product will help the users in booking transportation tickets by entering into appropriate websites, find the best airlines or trains as per the plan, allows users to select the preferred operator, fills out forms, proceed to the payment page for the user to complete the transaction. 
### 4.	Track Spending
What more could fear a person rather than not tracking his/her spendings. This is where the AI powered tracker comes in handy. With all bills and entries from the users, the product keep tracks of all the expenses in a separate database to visualize the spendings categorical wise to show a clear picture of the spending habit during the trip.
 
### 5.	Personal Assistant
During the trip, a dedicated caretaker will be assigned to each user group to guide them throughout the tour. Users could ask about the current place they are at, best restaurants nearby, does a particular place have car parking facility, will this place need an entrance ticket, etc. Think it as a personal guide that knows everything about that place.
### 6.	Helpdesk
What if my flight has been cancelled or if I need to reschedule it or make alternative changes to my plans. We have helpdesk that handles cancellation of tickets, plan changes, emergency assistance, etc.
## Role of AI Agents:
### 1.	Enquiry Agent
The general enquiry is handled by an agent that leverages the power of APIs to gather information from various sources that makes it suitable to answer all user queries and make them able to decide on their next vacation plan.
### 2.	Caretaker Agent
Once the trip has been planned, a dedicated AI agent helps in guiding the entire trip, gathering all attractions, hotels, resorts, and other information to act as a personal assistant.
### 3.	Travel Agent
This agent helps in deciding the optimal mode of transportation for the trip, lists out the best choices for the users to decide, fill forms automatically.
### 4.	Accommodation Agent
This agent helps in booking hotels and resorts.
### 5.	Helpdesk Agent
The helpdesk module is taken care by a separate agent 
### 6.	Tracker Agent
This agent helps users keep track off all the amount spent and enlightens them about how to save money.
# Workflow:
The user first registers to the product, enter their details which is stored in a MongoDB database. After that they land in a homepage where they can have a few options to select from.
1.	Create a Trip
2.	History
3.	Saved Plans
4.	Explore

At first let’s talk about the explore module in detail. In this module the user is just deciding their destination for their trip. So the Enquiry agent does all the work in guiding the user to their rightful place by asking a few questions like the country they want to go / the theme they prefer / the climate they would like to feel. This makes the agent understand the traveler’s mood and suggests some best locations. And since the agent has access to current climatic conditions and access to the web, it can also provide with weather insights and access restrictions to places if any due to unavoidable circumstances. So this helps the user to finalize a destination. Once the location is decided, a new trip is created and multiple agents will come in handy here. At first the caretaker agent interacts with the users to decide all locations and plans. The travel dates, the destinations, the time, the entire itinerary list is stored in MongoDB database as separate documents under a dedicated collection for cloud-based access. So once the list is finalized, it is time to make travel arrangements. Here the AI will help the users to list down the best way for transportation, fill out forms. This is all done with the help of API and form filling tools. Then the caretaker agent will guide the travelers throughout the trip. And since it has access to the user’s location, it can suggest a few places that are near to the user’s current location so that they don’t miss out on something wonderful and hidden. So no matter if the suggested place is not on the itinerary list, you do have a chance to have a look into it. All the chats made after creating the trip, the list, the amount spent, are all stored in database for future references. So overall people could use this product to plan their travel, save them for future use, or actually start their journey or could simply explore.


=======
# Tour_Guide
A LLM based tourist guide application leveraging multiple AI agents and databases.
 
# LLM Travel Assistant

## Description
This product helps users travel to a location with ease using AI. Users can enquire about traveling to a location, get travel insights like the ideal budget needed to visit the place, popular tourist attractions, rules and regulations, and interact with a chatbot. This helps users plan their trip to make it a memorable one. The product assists not only in the initial planning phase but also throughout the journey.

## Features

### 1. General Enquiry
Not all users have a particular location in mind. Some may have questions before confirming a spot, or just want to explore a new place. This component helps all kinds of users get a clear picture of when and where to go. For example:
- Is it safe to go to a hill station next month considering the weather conditions?
- I want to visit famous monuments in Spain as a group of 5. What would be the ideal budget and a 5-day plan?

With the help of APIs and up-to-date information, the AI chatbot provides accurate and satisfactory results.

### 2. Trip Planning
Once a location is finalized, the dates, budget, and locations to visit are discussed. The itinerary is created and modified according to user preferences. The AI suggests modifications to make the trip more valuable.

### 3. Ticket Booking
After planning, the product helps users book transportation tickets by accessing appropriate websites, finding the best airlines or trains, allowing users to select operators, filling out forms, and proceeding to payment.

### 4. Track Spending
The AI-powered tracker keeps track of all expenses in a separate database, visualizing spending by category to show a clear picture of spending habits during the trip.

### 5. Personal Assistant
During the trip, a dedicated caretaker is assigned to each user group to guide them. Users can ask about their current place, best restaurants nearby, parking facilities, entrance tickets, etc. Think of it as a personal guide that knows everything about the place.

### 6. Helpdesk
Handles flight cancellations, rescheduling, plan changes, emergency assistance, and more.

## Role of AI Agents

- **Enquiry Agent:** Handles general enquiries using APIs to gather information and answer user queries.
- **Caretaker Agent:** Guides the trip, gathers information on attractions, hotels, and acts as a personal assistant.
- **Travel Agent:** Decides the optimal mode of transportation, lists choices, and fills forms automatically.
- **Accommodation Agent:** Helps in booking hotels and resorts.
- **Helpdesk Agent:** Manages the helpdesk module.
- **Tracker Agent:** Tracks all spending and provides money-saving insights.

## Workflow

1. **User Registration:** Users register and enter their details, which are stored in a MongoDB database.
2. **Homepage Options:**
	- Create a Trip
	- History
	- Saved Plans
	- Explore

### Explore Module
In this module, the user decides their destination. The Enquiry Agent guides the user by asking about preferred country, theme, or climate. The agent suggests the best locations, provides weather insights, and informs about access restrictions. Once a location is decided, a new trip is created and multiple agents assist:
- The Caretaker Agent helps finalize the itinerary, which is stored in MongoDB.
- The Travel Agent assists with travel arrangements and form filling.
- The Caretaker Agent guides travelers during the trip, suggesting nearby places based on the user's location.

All chats, lists, and spending are stored in the database for future reference. Users can plan, save, or start their journey, or simply explore.
>>>>>>> Stashed changes
