function generateApplicationsForAllScenarios(modelName)
    % This function retrieves all scenarios from the Signal Editor in the root of the model
    % and generates a Simulink Real-Time application for each scenario
    %
    % Input:
    % modelName - The name of the Simulink model

    % Get all scenarios from the Signal Editor
    scenarios = getAllScenarios(modelName);

    % Loop through each scenario and generate the corresponding application
    for i = 1:length(scenarios)
        scenarioName = scenarios{i};

        % Change to the current scenario
        changeScenario(modelName, scenarioName);

        % Generate the application name
        appName = [modelName, '_', scenarioName];

        % Create the Simulink Real-Time application
        createRealTimeApplication(modelName, appName);
    end
end
