function changeScenario(signalEditorModel, scenarioName)
    % This function changes the active scenario in the Signal Editor of a given Simulink model
    %
    % Inputs:
    % signalEditorModel - The name of the Simulink model with the Signal Editor block
    % scenarioName - The name of the scenario to activate

    % Load the Simulink model if it's not already loaded
    if ~bdIsLoaded(signalEditorModel)
        load_system(signalEditorModel);
    end

    % Get the Signal Editor block path
    signalEditorBlocks = find_system(signalEditorModel, 'BlockType', 'SignalEditor');
    if isempty(signalEditorBlocks)
        error('No Signal Editor block found in the model.');
    end
    signalEditorBlock = signalEditorBlocks{1};

    % Get the current active scenario
    activeScenario = Simulink.ScenarioConfiguration.getActiveConfiguration(signalEditorBlock);

    % Get all scenarios in the Signal Editor block
    allScenarios = Simulink.ScenarioConfiguration.getConfigurations(signalEditorBlock);

    % Check if the specified scenario exists
    scenarioExists = any(strcmp({allScenarios.Name}, scenarioName));
    if ~scenarioExists
        error('The specified scenario does not exist.');
    end

    % Set the specified scenario as active
    Simulink.ScenarioConfiguration.setActiveConfiguration(signalEditorBlock, scenarioName);

    % Save the changes
    save_system(signalEditorModel);
    disp(['Scenario "', scenarioName, '" is now active in the model "', signalEditorModel, '".']);
end
