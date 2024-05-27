function str = decodeUTF8_prealloc(utf8_encoded)
    % Estimate the maximum number of characters
    maxNumChars = length(utf8_encoded);
    
    % Preallocate the output array
    str = repmat(' ', 1, maxNumChars);
    
    i = 1;
    j = 1;
    while i <= length(utf8_encoded)
        byte1 = utf8_encoded(i);
        
        if byte1 <= 127
            % 1-byte character
            code_point = byte1;
            num_bytes = 1;
        elseif bitand(byte1, 224) == 192
            % 2-byte character
            byte2 = utf8_encoded(i + 1);
            code_point = bitor(bitshift(bitand(byte1, 31), 6), bitand(byte2, 63));
            num_bytes = 2;
        elseif bitand(byte1, 240) == 224
            % 3-byte character
            byte2 = utf8_encoded(i + 1);
            byte3 = utf8_encoded(i + 2);
            code_point = bitor(bitshift(bitand(byte1, 15), 12), ...
                               bitor(bitshift(bitand(byte2, 63), 6), ...
                                     bitand(byte3, 63)));
            num_bytes = 3;
        else
            % 4-byte character
            byte2 = utf8_encoded(i + 1);
            byte3 = utf8_encoded(i + 2);
            byte4 = utf8_encoded(i + 3);
            code_point = bitor(bitshift(bitand(byte1, 7), 18), ...
                               bitor(bitshift(bitand(byte2, 63), 12), ...
                                     bitor(bitshift(bitand(byte3, 63), 6), ...
                                           bitand(byte4, 63))));
            num_bytes = 4;
        end
        
        % Append the decoded character to the string
        str(j) = char(code_point);
        
        % Move to the next set of bytes and increment character index
        i = i + num_bytes;
        j = j + 1;
    end
    
    % Trim the unused portion of the preallocated array
    str = str(1:j-1);
end
