<%page args="address, county, neighborhood, coordinates, propertyindex" />

%if propertyindex is not None:
    <h2>Property ${propertyindex}</h2>
%else:
    <h2>Property information</h2>
%endif

<table>
    <tr><th>Address:</th><td>${address}</td></tr>
    <tr><th>County:</th><td>${county}</td></tr>
    <tr><th>Neighborhood:</th><td>${neighborhood}</td></tr>
    <tr><th>Coordinates:</th><td>${coordinates}</td></tr>
</table>
