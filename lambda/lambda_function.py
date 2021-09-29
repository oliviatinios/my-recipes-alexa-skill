# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from botocore.vendored import requests


from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


BACKEND_URL = 'http://myrecipesapi-env.eba-fqpk9meu.us-east-1.elasticbeanstalk.com'


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to my recipes. Say, start my recipe, to begin."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetRecipeByNameHandler(AbstractRequestHandler):
    """Handler for Get Recipe By Name Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetRecipeByName")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # get recipe title from request object
        slots = handler_input.request_envelope.request.intent.slots
        recipe_title = slots['Title']
        
        # Login to My Recipes account and store authentication token
        # TODO: add account linking
        data = { 'email' : 'oliviatinios@gmail.com', 'password' : 'Banana123!' }
        try: 
            res = requests.post(url = BACKEND_URL + '/users/login', json=data)
        except:
            logger.error(exception, exc_info=True)
        auth_token = res.json().get('token')
        
        # Search for recipe by title
        headers = { 'Authorization': 'Bearer {}' .format(auth_token) }
        params = { 'title' : recipe_title.value.lower() }
        try: 
            res = requests.get(url = BACKEND_URL + '/recipes', headers = headers, params = params)
        except:
            logger.error(exception, exc_info=True)
        recipes = res.json()
        
        # Check if response is empty
        if len(recipes) == 0:
            speak_output = 'You have no recipe with that name. Please try a different one.'
        else:
            # TODO: ask user which recipe they would like to access
            recipe = recipes[0]
            speak_output = '{}. This recipe has {} ingredients and {} steps. It takes {} minutes to prepare.' .format(recipe.get('description'), len(recipe.get('ingredients')), len(recipe.get('steps')), recipe.get('totalTime'))

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class StartRecipeHandler(AbstractRequestHandler):
    """Handler for Start Recipe Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StartRecipe")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # get recipe title from request object
        slots = handler_input.request_envelope.request.intent.slots
        recipe_title = slots['Title']
        
        # Login to My Recipes account and store authentication token
        data = { 'email' : 'oliviatinios@gmail.com', 'password' : 'Banana123!' }
        try: 
            res = requests.post(url = BACKEND_URL + '/users/login', json=data)
        except:
            logger.error(exception, exc_info=True)
        auth_token = res.json().get('token')
        
        # Search for recipe by title
        headers = { 'Authorization': 'Bearer {}' .format(auth_token) }
        params = { 'title' : recipe_title.value.lower() }
        try: 
            res = requests.get(url = BACKEND_URL + '/recipes', headers = headers, params = params)
        except:
            logger.error(exception, exc_info=True)
        recipes = res.json()
        
        # Check if response is empty
        if len(recipes) == 0:
            speak_output = 'You have no recipe with that name. Please try a different one.'
        else:
            # TODO: ask user which recipe they would like to access
            recipe = recipes[0]
            # store the recipe  and the current_step in session attributes
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr['recipe'] = recipe
            session_attr['current_step'] = 0
            speak_output = 'Starting your {} recipe. It has {} ingredients and {} steps. When you are ready to begin the first step, just say, get first step, or, get next step.' .format(recipe.get('title'), len(recipe.get('ingredients')), len(recipe.get('steps')))

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetFirstStepIntentHandler(AbstractRequestHandler):
    """Handler for Get First Step Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetFirstStep")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Get first step from session attributes
        session_attr = handler_input.attributes_manager.session_attributes
        
        if not(session_attr.get('recipe')):
            speak_output = 'You have not started a recipe yet. Say start recipe to begin.'
            
        elif not(session_attr.get('recipe')['steps']):
            speak_output = 'Your recipe has no steps. You can add steps in the my recipes app.'
            
        else:
            speak_output = '{}' .format(session_attr.get('recipe')['steps'][0]['value'])
            # increment the current step in session attributes
            session_attr['current_step'] = 0
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetCurrentStepIntentHandler(AbstractRequestHandler):
    """Handler for Get Current Step Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetCurrentStep")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Get first step from session attributes
        print('test')
        session_attr = handler_input.attributes_manager.session_attributes
        
        if not(session_attr.get('recipe')):
            speak_output = 'You have not started a recipe yet. Say start recipe to begin.'
            
        elif not(session_attr.get('recipe')['steps']):
            speak_output = 'Your recipe has no steps. You can add steps in the my recipes app.'
            
        else:
            # if current step not already set, set to 0
            if not(session_attr.get('current_step')):
                session_attr['current_step'] = 0
            
            current_step_index = session_attr.get('current_step')
                
            speak_output = '{}' .format(session_attr.get('recipe')['steps'][current_step_index]['value'])
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetNextStepIntentHandler(AbstractRequestHandler):
    """Handler for Get Next Step Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetNextStep")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Get first step from session attributes
        session_attr = handler_input.attributes_manager.session_attributes
        
        if not(session_attr.get('recipe')):
            speak_output = 'You have not started a recipe yet. Say start recipe to begin.'
            
        elif not(session_attr.get('recipe')['steps']):
            speak_output = 'Your recipe has no steps. You can add steps in the my recipes app.'
            
        # if current step not already set, set to 0
        elif not('current_step' in session_attr):
            session_attr['current_step'] = 0
            speak_output = '{}' .format(session_attr.get('recipe')['steps'][session_attr.get('current_step')]['value'])
                
        # check if already at last step
        elif session_attr.get('current_step') == len(session_attr.get('recipe')['steps']) - 1:
            speak_output = 'You are already at the last step. Say, get first step, to go to the beginning, or, get previous step, to go back one.'
                
        else:
            # increment current step
            session_attr['current_step'] = session_attr.get('current_step') + 1
            speak_output = '{}' .format(session_attr.get('recipe')['steps'][session_attr.get('current_step')]['value'])
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetPreviousStepIntentHandler(AbstractRequestHandler):
    """Handler for Get Previous Step Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetPreviousStep")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Get first step from session attributes
        session_attr = handler_input.attributes_manager.session_attributes
        
        if not(session_attr.get('recipe')):
            speak_output = 'You have not started a recipe yet. Say start recipe to begin.'
            
        elif not(session_attr.get('recipe')['steps']):
            speak_output = 'Your recipe has no steps. You can add steps in the my recipes app.'
            
        # if current step not already set, set to 0
        elif not('current_step' in session_attr):
            session_attr['current_step'] = 0
            speak_output = '{}' .format(session_attr.get('recipe')['steps'][session_attr.get('current_step')]['value'])
                
        # check if already at first step
        elif session_attr.get('current_step') == 0:
            speak_output = 'You are already at the first step. Say, get next step, to go to the next step.'
                
        else:
            # decrement current step
            session_attr['current_step'] = session_attr.get('current_step') - 1
            speak_output = '{}' .format(session_attr.get('recipe')['steps'][session_attr.get('current_step')]['value'])
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetIngredientsIntentHandler(AbstractRequestHandler):
    """Handler for Get Ingredients Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetIngredients")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Get first step from session attributes
        session_attr = handler_input.attributes_manager.session_attributes
        
        if not(session_attr.get('recipe')):
            speak_output = 'You have not started a recipe yet. Say start recipe to begin.'
            
        elif not(session_attr.get('recipe')['ingredients']):
            speak_output = 'Your recipe has no ingredients. You can add ingredients in the my recipes app.'
            
        else:
            ingredients = [ ingredient.get('value') for ingredient in session_attr.get('recipe')['ingredients'] ]
            speak_output = "{}" .format(ingredients)
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetRecipeByNameHandler())
sb.add_request_handler(StartRecipeHandler())
sb.add_request_handler(GetFirstStepIntentHandler())
sb.add_request_handler(GetCurrentStepIntentHandler())
sb.add_request_handler(GetNextStepIntentHandler())
sb.add_request_handler(GetPreviousStepIntentHandler())
sb.add_request_handler(GetIngredientsIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()