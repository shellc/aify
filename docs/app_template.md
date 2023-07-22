# # App template

Aify uses YAML files to define applications. Applications are reusable, and we also call YAML-formatted applications templates. Template files consist of the following parts:

* Application descriptions
* Model settings 
* Modules 
* Prompt 
* Variables 

## Application description 

The application description contains attribute fields used to explain basic information about the application:

* `title`: The title of the application, used for display and identification in the interface 
* `description`: A text that explains the functionality of the application, generally not too long. The built-in chatbot in Aify will display this text on the application list card, not required 
* `version`: Used to indicate the current version of the application, not required 
* `author`: The author of the application, not required 
* `website`: The website of the application author, not required 
* `email`: The author's email, not required 
* `license`: The open-source license of the author, not required 

## Model 

The model specifies the AI model used by the application, mainly LLMs and Transformers models. An example of model settings is as follows:

```
model: 
	type: llm 
	vendor: openai 
	name: gpt-3.5-turbo 
	params: 
		api_key: sk-xxxxx
```

Supported model list:

* openai 
	* llm 
		* models: 
			* gpt-3.5-turbo* 
			* gpt-4* 
		* params: 
			* api_key 
			* api_base 

## Modules 

Modules are Python modules loaded during the runtime of the application, which can extend the capabilities of the application. For example:

```
modules: 
	memory: $AIFY_MEMORY_STORAGE 
	my_memory_storate: my.memory_storage 
	helpers: helpers 
```

Several things happen here:

1. We override the default memory implementation with the value represented by the environment variable AIFY_MEMORY_STORAGE. 
2. We define our own my.memory_storage module, using our own backend storage to store memories. 
3. We define the helpers module, which contains some useful functions. 

The modules defined here can be called during the runtime of the application.

## Prompt 

The prompt defines the flow of the program. Since Aify uses guidance as the engine, the definition and format of this part are completely the same as guidance. We include the prompt definition in our application template to make it part of our application. The benefit is that we can directly call extension modules in the prompt to enhance the program's capabilities.

The prompt template syntax of guidance is Handlebars. For details about guidance and Handlebars, please refer to their documentation:

* Handlebars template syntax: [https://handlebarsjs.com/](https://handlebarsjs.com/)
* guidance extension functions: [https://guidance.readthedocs.io/en/latest/api.html#program-creation-a-k-a-guidance-program-string](https://guidance.readthedocs.io/en/latest/api.html#program-creation-a-k-a-guidance-program-string) 


## Variables 

Variables define the input and output of the application, making it easier for higher-level applications to handle and interact with the application. The RESTful API and built-in chatbot only output the defined variables.

The format for defining variables is as follows:

```
variables:
	- name: prompt 
	  type: input 
	  data_type: string 
	  required: true
	- name: answer 
	  type: output 
	  data_type: string 
	  required: true 
```

These definitions can be retrieved through the API for higher-level applications to customize the interface.