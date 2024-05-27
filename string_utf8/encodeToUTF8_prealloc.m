function utf8_encoded = encodeToUTF8_prealloc(str)
    % Calculate the required size for the output array
    numBytes = 0;
    for i = 1:length(str)
        code_point = double(str(i));
        if code_point <= 127
            numBytes = numBytes + 1; % 1-byte character
        elseif code_point <= 2047
            numBytes = numBytes + 2; % 2-byte character
        elseif code_point <= 65535
            numBytes = numBytes + 3; % 3-byte character
        else
            numBytes = numBytes + 4; % 4-byte character
        end
    end
    
    % Preallocate the output array
    utf8_encoded = zeros(1, numBytes, 'uint8');
    
    % Encode the string to UTF-8
    idx = 1;
    for i = 1:length(str)
        code_point = double(str(i));
        if code_point <= 127
            utf8_encoded(idx) = code_point; % 1-byte character
            idx = idx + 1;
        elseif code_point <= 2047
            utf8_encoded(idx) = bitor(192, bitshift(code_point, -6));
            utf8_encoded(idx + 1) = bitor(128, bitand(code_point, 63));
            idx = idx + 2;
        elseif code_point <= 65535
            utf8_encoded(idx) = bitor(224, bitshift(code_point, -12));
            utf8_encoded(idx + 1) = bitor(128, bitand(bitshift(code_point, -6), 63));
            utf8_encoded(idx + 2) = bitor(128, bitand(code_point, 63));
            idx = idx + 3;
        else
            utf8_encoded(idx) = bitor(240, bitshift(code_point, -18));
            utf8_encoded(idx + 1) = bitor(128, bitand(bitshift(code_point, -12), 63));
            utf8_encoded(idx + 2) = bitor(128, bitand(bitshift(code_point, -6), 63));
            utf8_encoded(idx + 3) = bitor(128, bitand(code_point, 63));
            idx = idx + 4;
        end
    end
end
