function createRealTimeApplication(modelName, appName)
    % This function compiles a Simulink model and creates a Simulink Real-Time application with a specified name
    %
    % Inputs:
    % modelName - The name of the Simulink model to compile
    % appName - The name of the Simulink Real-Time application to create

    % Load the Simulink model if it's not already loaded
    if ~bdIsLoaded(modelName)
        load_system(modelName);
    end

    % Set the target to Simulink Real-Time
    set_param(modelName, 'SystemTargetFile', 'slrt.tlc');

    % Set the application name
    set_param(modelName, 'RTWSystemTargetFile', 'slrt.tlc', 'RTWGenerateCodeOnly', 'off');
    slbuild(modelName, 'StandaloneRTW', 'Name', appName);

    % Optionally, save the changes to the model
    save_system(modelName);

    disp(['Real-Time application "', appName, '" created for model "', modelName, '".']);
end
