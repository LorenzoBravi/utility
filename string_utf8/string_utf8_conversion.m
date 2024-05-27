% Define the string
original_str = 'Hello, world!';

% Encode the string to UTF-8
utf8_encoded = encodeToUTF8(original_str);

% Display the encoded result
disp('Encoded:');
disp(utf8_encoded);

% Decode the UTF-8 encoded bytes back to string
decoded_str = decodeUTF8(utf8_encoded);

% Display the decoded result
disp('Decoded:');
disp(decoded_str);
