# CS-50-project-durham-info-finder

****DURHAM ADDRESS LOOKUP TOOL****

This project allows a new resident of Durham, NC to enter their address and be
returned information they might need when moving to their new residence. In addition
to information on connecting utlilities, the site sends the user's address to an
API that returns their geographic cooordinates.  The program then compares these
coordinates to those found in the durham_info database to find the nearest hospital,
library and the closest "location of interest" such as a store or restaurant. All
items are then displayed to the user on the results.html page.

The user is also prompted for feedback on this location.  If they like it, they are
thanked for their feedback.  If they don't like it,they are provided the next
closest location.  The database keeps track for the user feedback and will flag a
location to not be provided to users if it has three more dislikes than likes.
The program contains validation to to make sure the user provides a good durham
address and also has a helper funtion to format the users street address to be
spelled and foramtted correctly when returned on the results page.
