function scenarios = getAllScenarios(signalEditorModel)
    % This function retrieves all scenarios from the Signal Editor of a given Simulink model
    %
    % Inputs:
    % signalEditorModel - The name of the Simulink model with the Signal Editor block
    %
    % Outputs:
    % scenarios - A cell array of scenario names

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

    % Get all scenarios in the Signal Editor block
    allScenarios = Simulink.ScenarioConfiguration.getConfigurations(signalEditorBlock);

    % Extract the names of all scenarios
    scenarios = {allScenarios.Name};

    % Display the scenarios
    disp('Available scenarios:');
    disp(scenarios);
end
