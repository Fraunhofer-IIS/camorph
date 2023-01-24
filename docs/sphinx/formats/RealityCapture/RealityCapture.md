# Reality Capture

*Reality Capture* is a 3D reconstruction software developed by Epic
Games, Inc. There are several possibilities to export cameras: XMP, csv
and FBX. Camorph supports the XMP file format, as this is the
only format supported for importing cameras. *Reality Capture* generates
XMP files for every source image in the source image folder. When you
create a new *Reality Capture* project, XMP files in the source image
folder with the same name as the images are imported automatically

## Coordinate System

*Reality Capture* supports alignment with all EPSG geodesic coordinate
systems. In Cartesian world coordinates, it uses z up,
x right, -y front. The default orientation for cameras
is z front and -y up. Yaw, Pitch and Roll in *Reality
Capture* correspond to a rotation around the $z$,$y$ and
$x$-axis respectively. Usually, angles are measured in
counterclockwise direction around an axis. But in *Reality Capture*,
Yaw is measured clockwise. This means that yaw = 180 - yaw to correct
for counterclockwise orientation.The resulting rotation matrix with $z$ = yaw = $\phi$,
$y$ = pitch = $\theta$ and $x$ = roll = $\psi$
*Reality Capture* uses internally:

$$
\begin{pmatrix}
\cos{\psi}\cos{\phi} + \sin{\psi}\sin{\theta}\sin{\phi} & -\cos{\psi}\sin{\phi} + \cos{\phi}\sin{\psi}\sin{\theta} & -\cos{\theta}\sin{\psi} \\
-\cos{\theta}\sin{\phi} & -\cos{\theta}\cos{\phi} & -\sin{\theta} \\
\cos{\psi}\sin{\theta}\sin{\phi} - \cos{\phi}\sin{\psi} & \cos{\psi}\cos{\phi}\sin{\theta} + \sin{\psi}\sin{\phi} & -\cos{\psi}\cos{\theta}
\end{pmatrix}
$$

When comparing this matrix to “regular” rotation matrices, note that the only difference to the
rotation matrix $R_{zxy}$ is that $\cos{\theta}$ is
$-\cos{\theta}$. This occurs because
$\theta = \pi - \theta_{RC}$, as mentioned above. This also
means that the rotational order *Reality Capture* uses internally is
$z-x-y$ , or $R_y \cdot R_x \cdot R_z$. This is only
relevant when dealing with .csv files, as the exported angles are the
angles displayed in *Reality Capture*. The XMP files already supply
the “correct” rotational matrix.



![image](./RealityCapture_coordinatesystem_cam-1.png)

## XMP Files

XMP is a file format based on the [Resource Description Framework](https://www.w3.org/RDF/) (rdf).

The `rdf:Description` element has the following important
attributes:


* `DistortionModel` is the name of the distortion model type


* `FocalLength35mm` is the focal length with respect the 135 film
standard


* `Skew` is the skew parameter in the intrinsic matrix


* `AspectRatio` is the pixel aspect ratio, not the sensor aspect
ratio, which is 1 most of the time


* `PrincipalPointU` and `PrincipalPointV` are the principal point
coordinates relative to the middle of the image plane and the
resolution

This element contains three additional elements:


* `Rotation` which is the rotational matrix in row major order.
It is the inverse of
$R$, meaning the rotational matrix used in the projection
equation.


* `Position` is the center of the camera


* `DistortionCoeficients`(sic) are six distortion parameters based
on the `DistortionModel`. There are always six coefficients, with
unused parameters being zero.

## Camera Models

*Reality Capture* always stores six distortion coefficients. When the
camera model does not support six parameters, the unused parameters are
set to zero. The camera models supported by *Reality Capture* are:

<table class="docutils align-default"><colgroup><col style="width: 22%"> <col style="width: 41%"> <col style="width: 38%"></colgroup> 

<thead>

<tr class="row-odd">

<th class="head">

**Name**

</th>

<th class="head">

**Description**

</th>

<th class="head">

**Parameters**

</th>

</tr>

</thead>

<tbody>

<tr class="row-even">

<td>

`brown3`

</td>

<td>

Brown distortion model with three radial parameters

</td>

<td>

k1, k2, k3, 0, 0, 0

</td>

</tr>

<tr class="row-odd">

<td>

`brown4`

</td>

<td>

Brown distortion model with four radial parameters

</td>

<td>

k1, k2, k3, k4, 0, 0

</td>

</tr>

<tr class="row-even">

<td>

`brown3t2`

</td>

<td>

Brown distortion model with three radial parameters and two tangential parameters

</td>

<td>

k1, k2, k3, 0, t1, t2

</td>

</tr>

<tr class="row-odd">

<td>

`brown4t2`

</td>

<td>

Brown distortion model with four radial parameters and two tangential parameters

</td>

<td>

k1, k2, k3, k4, t1, t2

</td>

</tr>

<tr class="row-even">

<td>

`division`

</td>

<td>

Division distortion model

</td>

<td>

k, 0, 0, 0, 0, 0

</td>

</tr>

</tbody>

</table>