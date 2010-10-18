!------------------------------------------------------------------------------

module micrometeo

character*6 spec_mmeteo  ! for mmeteo


! Input meteorological data at current time step

integer :: ntime
real :: day,hour    ! day and hour
real, allocatable :: glob(:), diff(:), direct(:), dsg (:) ! global, diffuse and direction radiation in band iblo, D/G ratio in band iblo
real :: ratmos      ! atmospheric radiation
real :: tsol,taref,earef,caref ! soil temperature, air temperature, water vapour pressure in the air (Pa), CO2 partial pressure in the air (Pa)
real, allocatable :: uref(:)  ! wind speed, in each horizontal layer (jz=1,njz)
logical  :: endmeteo     ! TRUE if end of mmeteo file has been reached

contains

 subroutine mm_initiate

!  Allocate arrays of module micrometeo

  use grid3D
  use vegetation_types

  call mm_destroy

  allocate(glob(nblomin))
  allocate(diff(nblomin))
  allocate(direct(nblomin))
  allocate(dsg(nblomin))

  allocate(uref(njz))

  endmeteo=.FALSE.

 end subroutine mm_initiate

 subroutine mm_read(ntime,pathMeteo,spec)
  use grid3D
  use vegetation_types

  character*17 pathMeteo
  character*6 spec

  logical :: linenotread

  call mm_initiate


  open (4,file=pathMeteo//spec)
  linenotread = .true.
   do i=1,ntime
    !write(*,*) 'i=',i
    read(4,*,end = 998)  ! Skip ntime lines, i.e. header (1st line) + (ntime - 1) data lines
   end do

   do while(linenotread)
   read(4,*,end = 998) day,hour,(glob(iblo),diff(iblo),iblo=1,nblomin), ratmos,tsol,taref,earef,caref,urefref
   !write(*,*) 'day,hour =',day,hour !,(glob(iblo),diff(iblo),iblo=1,nblomin), ratmos,tsol,taref,earef,caref,urefref
   linenotread = .false.
!   Rem: L'azimut 0 est défini pour la direction SUD,
!      i.e. un rayon avancant vers le NORD, donc les X > 0
!    L'azimut 90 est défini pour la direction OUEST,
!    i.e. un rayon avancant vers l'EST, donc les Y > 0

   !write(*,*)
   !write(*,*) '----------------------------------------'
   !write(*,*) 'Step: ',ntime

   do iblo=1,nblomin
    if (glob(iblo).gt.0.) then
     if (glob(iblo).lt.diff(iblo)) then
      !write(*,*) 'Warning: Incident radiation in waveband #',iblo,' is lesser than value of diffuse radiation:'
      !write(*,*) glob(iblo),' < ',diff(iblo)
      !write(*,*) 'Will be set to value of incident diffuse radiation:', diff(iblo)
!      pause
      glob(iblo)=diff(iblo)
     endif
     direct(iblo)=glob(iblo)-diff(iblo)
     dsg(iblo)=diff(iblo)/glob(iblo)
    else
     !write(*,*) 'Warning: Incident radiation in waveband #',iblo,' is negative or zero:', glob(iblo)
     !write(*,*) 'Will be set to zero'
!     pause
     glob(iblo)=0.
     diff(iblo)=0.
     direct(iblo)=0.
     dsg(iblo)=1.
    endif
   end do

   do jz=1,njz
    uref(jz) = urefref
   end do
   !write(*,*) 'end meteo'


  end do
  998 continue
  if (linenotread) then
    !write(*,*) 'End of mmeteo file reached: Job terminated'
    endmeteo=.TRUE.
  endif
  !write(*,*) 'close 4'
  close(4)


 end subroutine mm_read

 subroutine mm_destroy

!  Deallocate arrays of module micrometeo

  if (allocated(glob))  deallocate(glob)
  if (allocated(diff))  deallocate(diff)
  if (allocated(direct)) deallocate(direct)
  if (allocated(dsg))  deallocate(dsg)

  if (allocated(uref))  deallocate(uref)

 end subroutine mm_destroy


end module micrometeo

!------------------------------------------------------------------------------
