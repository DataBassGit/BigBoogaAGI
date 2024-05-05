from agentforge.agent import Agent


class StopExecution(Exception):
    """
    Custom exception to signal a stop in the agent's execution flow, particularly when no relevant action is found.
    """
    pass


class ActionSelectionAgent(Agent):
    actions = {}
    threshold = 0.6  # Threshold value for action selection.
    num_results = 10  # Number of results to be considered in the action selection process.

    def run(self, **kwargs):
        """
        Executes the agent's run cycle with enhanced error handling to catch a StopExecution exception.

        Parameters:
            **kwargs: Arbitrary keyword arguments passed to the base run method.

        Returns: The output generated by the agent or None if a StopExecution exception is caught, indicating no
        relevant action was found.
        """
        try:
            return super().run(**kwargs)
        except StopExecution:
            self.logger.log_result('No Relevant Action Found', 'Selection Results')
            return None

    def load_additional_data(self):
        """
        Overrides the base class method to load additional, action-related data specific to this agent.
        """
        try:
            self.load_actions()
        except Exception as e:
            self.logger.log(f"Error loading additional data: {e}", 'error')

    def load_actions(self):
        """
        Loads actions based on the current task and specified criteria from the storage system.
        """
        try:
            self.actions = self.storage.search_storage_by_threshold(collection_name='Actions',
                                                                    query_text=self.data['task'],
                                                                    threshold=self.threshold,
                                                                    num_results=self.num_results)
        except Exception as e:
            self.logger.log(f"Error loading actions: {e}", 'error')
            self.actions = {}

    def process_data(self):
        """
        Overrides the base method to integrate custom action processing logic, including stopping execution if no
        action is found.
        """
        try:
            self.stop_execution_on_no_action()
            self.parse_actions()
            self.format_actions()
        except Exception as e:
            self.logger.log(f"Error processing data: {e}", 'error')

    def stop_execution_on_no_action(self):
        """
        Raises a StopExecution exception if no actions were found that meet the specified criteria.
        """
        if 'failed' in self.actions:
            raise StopExecution("No actions found, stopping execution.")

    def parse_actions(self):
        """
        Parses and structures the actions fetched from storage for easier handling and processing.
        """
        parsed_actions = {}
        try:
            if 'failed' not in self.actions:
                for metadata in self.actions.get("metadatas", [])[0]:
                    action_name = metadata.get("Name")
                    if action_name:
                        metadata.pop('timestamp', None)  # Remove any non-relevant metadata, such as timestamps
                        parsed_actions[action_name] = metadata
                self.actions = parsed_actions
        except Exception as e:
            self.logger.log(f"Error Parsing Actions:\n{self.actions}\n\nError: {e}", 'error')
            self.actions = {}

    def format_actions(self):
        """
        Formats the actions into a human-readable string and stores it in the agent's data for later use.
        """
        try:
            if 'failed' not in self.actions:
                formatted_actions = []
                for action_name, metadata in self.actions.items():
                    action_desc = metadata.get("Description", "No Description")
                    formatted_action = f"Action: {action_name}\nDescription: {action_desc}\n"
                    formatted_actions.append(formatted_action)
                self.data['action_list'] = "\n".join(formatted_actions)
        except Exception as e:
            self.logger.log(f"Error Formatting Actions:\n{self.actions}\n\nError: {e}", 'error')

    def parse_result(self):
        """
        Parses the result from YAML format into a Python dictionary for further processing.
        """
        try:
            self.result = self.functions.agent_utils.parse_yaml_string(self.result)
        except Exception as e:
            self.logger.parsing_error(self.result, e)

    def save_result(self):
        """
        Overrides the save_result method from the Agent class. This method is left empty, as this agent does not
        require saving results to memory.
        """
        pass

    def build_output(self):
        """
        Constructs the final output by selecting an action based on the result of the language model's generation.
        """
        try:
            selected_action = self.result['action']
            if selected_action in self.actions:
                self.output = self.actions[selected_action]
                return

            self.output = (f"The '{selected_action}' action does not exist. It is very likely the agent did not "
                           f"correctly choose an action from the given list.")
        except Exception as e:
            self.logger.parsing_error(self.result, e)

    def set_number_of_results(self, new_num_results):
        """
        Sets a new number of results to be considered in the action selection process.

        Parameters:
            new_num_results (int): The new number of results to fetch and consider for action selection.
        """
        self.num_results = new_num_results

    def set_threshold(self, new_threshold):
        """
        Sets a new threshold value for action selection.

        Parameters:
            new_threshold (float): The new threshold value for determining relevancy of actions.
        """
        self.threshold = new_threshold
