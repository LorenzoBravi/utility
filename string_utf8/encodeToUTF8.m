function utf8_encoded = encodeToUTF8(str)
    % Initialize an empty array to hold the UTF-8 encoded bytes
    utf8_encoded = [];

    % Loop through each character in the string
    for i = 1:length(str)
        % Get the Unicode code point of the character
        code_point = double(str(i));

        % Encode the code point to UTF-8
        if code_point <= 127
            utf8_encoded = [utf8_encoded, code_point]; % 1-byte character
        elseif code_point <= 2047
            utf8_encoded = [utf8_encoded, ...
                            bitor(192, bitshift(code_point, -6)), ...
                            bitor(128, bitand(code_point, 63))]; % 2-byte character
        elseif code_point <= 65535
            utf8_encoded = [utf8_encoded, ...
                            bitor(224, bitshift(code_point, -12)), ...
                            bitor(128, bitand(bitshift(code_point, -6), 63)), ...
                            bitor(128, bitand(code_point, 63))]; % 3-byte character
        else
            utf8_encoded = [utf8_encoded, ...
                            bitor(240, bitshift(code_point, -18)), ...
                            bitor(128, bitand(bitshift(code_point, -12), 63)), ...
                            bitor(128, bitand(bitshift(code_point, -6), 63)), ...
                            bitor(128, bitand(code_point, 63))]; % 4-byte character
        end
    end

    % Convert the result to uint8
    utf8_encoded = uint8(utf8_encoded);
end
