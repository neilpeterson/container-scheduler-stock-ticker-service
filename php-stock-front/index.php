<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <link href="Default.css" rel="stylesheet" />
    <title>Container Demo..</title>

    <script language="JavaScript">
        function send(form) {
        }

    </script>

</head>
<body>

    <div id="container">
        
        <div id="logo">Stock Report Generator</div>
        <div id="form">
                <form id="form" name="form" action="create-message.php" method="post"><center>
                <input id="symbols:" type="text" name="symbols" placeholder="Stock Symbols" /><br />
                <input id="email:" type="email address" name="email" placeholder="Email Address" /><br />
                <input id="beastmode" type="integer" name="beast" placeholder="Beast Mode" /><br />
                <input id="Submit:" type="submit" name="submit" placeholder="submit" value="Submit" /><br />
            </center>
            </form>
        </div>
    </div>
</body>
</html>