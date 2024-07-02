<?php
if ($argc !== 3) {
    echo 'Usage: php verify_password.php <password> <hash>';
    exit(1);
}

$password = $argv[1];
$hash = $argv[2];

if (password_verify($password, $hash)) {
    echo '1';
} else {
    echo '0';
}
?>
