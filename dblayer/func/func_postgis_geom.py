from sqlalchemy.sql import func
from collections import namedtuple


class Point2D( namedtuple( 'Point2D_Tuple', [ 'x', 'y' ] ) ):
    """
    Tuple for representing 2D points.

    Attributes:

    x, y (float): 2D coordinates
    """

    __slots__ = ()

    def list( self ): return [ self.x, self.y ]


def geom_from_text(
    well_known_text,
    srid = None
    ):
    """
    Define function call for converting well-known text representation to PostGIS geometry object.

    :param well_known_text: well-known text representation of geometry (string)
    :return: SQL function (sqlalchemy.sql.functions.Function)
    """
    if ( srid is None ):
        return func.ST_GeomFromText( well_known_text )
    else:
        return func.ST_GeomFromText( well_known_text, srid )


def geom_from_2dpoint(
    point,
    srid = None
    ):
    """
    Define function call for converting 2D point to PostGIS geometry object.

    :param point: coordinates of 2D point (Point2D)
    :return: SQL function (sqlalchemy.sql.functions.Function)
    """
    if not isinstance( point, Point2D ):
        raise TypeError( 'parameter \'point\' must be of type \'Point2D\'' )

    # Construct well-known text representation of 2D point.
    well_known_text = 'POINT({x} {y} 0)'.format( x = point.x, y = point.y )

    return geom_from_text( well_known_text, srid )


def geom_from_2dlinestring(
    points,
    srid = None
    ):
    """
    Define function call for converting a 2D line to PostGIS geometry object.

    :param points: 2D points to be joined in a connected series of line segments (list of Point2D)
    :return: SQL function (sqlalchemy.sql.functions.Function)
    """
    if not all( isinstance( p, Point2D ) for p in points ):
        raise TypeError( 'parameter \'points\' must be of type \'list of Point2D\'' )

    # Construct well-known text representation of 2D linestring.
    coordinates = []
    for p in points:
        coordinates.append( '{x} {y} 0'.format( x = p.x, y = p.y ) )
    separator = ','
    well_known_text = 'LINESTRING({})'.format( separator.join( coordinates ) )

    return geom_from_text( well_known_text, srid )


def geom_from_2dpolygon(
    points,
    srid = None
    ):
    """
    Define function call for converting a 2D polygon to PostGIS geometry object.

    :param points: 2D points to be joined in a closed loop of line segments (list of Point2D)
    :return: SQL function (sqlalchemy.sql.functions.Function)
    """
    if not all( isinstance( p, Point2D ) for p in points ):
        raise TypeError( 'parameter \'points\' must be of type \'list of Point2D\'' )

    first_point = points[0]
    last_point = points[-1]
    if ( first_point.x != last_point.x ) or ( first_point.y != last_point.y ):
        raise ValueError( 'first and last point do not coincide' )

    # Construct well-known text representation of 2D polygon.
    coordinates = []
    for p in points:
        coordinates.append( '{x} {y} 0'.format( x = p.x, y = p.y ) )
    separator = ','
    well_known_text = 'POLYGON(({}))'.format( separator.join( coordinates ) )

    return geom_from_text( well_known_text, srid )


def geom_as_text(
    geometry
    ):
    """
    Define function call for converting PostGIS geometry object to well-known text representation.

    :param geometry: PostGIS geometry object (string)
    :return: SQL function (sqlalchemy.sql.functions.Function)
    """
    return func.ST_AsText( geometry )


def length_from_geom(
    geometry
    ):
    """
    Define function call for calculating length of PostGIS geometry object.

    :param geometry: PostGIS geometry object (string)
    :return: SQL function (sqlalchemy.sql.functions.Function)
    """
    return func.ST_Length( geometry )
