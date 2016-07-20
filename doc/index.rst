Party Zip Module
################

The Party Zip module adds the country zip field to addresses as well as menu
entries to Country Zip and Subdivision models.

If installed, the module will make zip and city fields in addresses readonly
so they can only be filled in with the new country zip field. This allows all
addresses to have a zip/city that is previously created in the database.

The module also takes care of updating all addresses if zip, city, subdivision
or country fields are changed in the zip record.
