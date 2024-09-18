### count_lables.py and count_images.py
In both the count files, replace the username, password, and project_id number. Replace the cvat host if you aren't using the hosted solution. This should return a count of the labels and images respectivly, associated with a project. 
For labels, the output will look like this:

Cat: 8
Dog: 4
Person: 2

Total: 14

count_images.py has a very similar output, but counts the number tagged for training, test, and validation (and any other categories you might have) and provides a total.

### cvat_assisted_labeling.py
Helper file for ML assisted annotation, use like so:
` cvat-cli --server-host app.cvat.ai --auth USERNAME auto-annotate 123456 --function-file .\cvat_assisted_labeling.py --allow-unmatched-labels --clear-existing`
Replacing USERNAME and 123456 (the Task ID number you wish to label). Password is stored in a system variable `$ENV:PASS = Read-Host -MaskInput` (PS7 required for the -MaskInput flag). More information here: https://www.youtube.com/watch?v=T68fQJNHG84
