"""
@file criminals/models.py
@brief Data models for the criminals app.

@details
Defines models for representing criminals and their associated offenses,
including both federal and Virginia Code violations. Supports linking
individuals to multiple types of offenses using an intermediary model.
"""

from django.db import models


class Criminal(models.Model):
    """
    @brief Model representing a criminal individual.

    @details
    Stores basic identity information about a criminal, including
    first name, last name, and optional date of birth.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        """
        @brief String representation combining first and last name.

        @details
        Returns the full name of the criminal for easy identification.

        @return str The full name of the criminal.
        """
        return f"{self.first_name} {self.last_name}"


class CriminalOffense(models.Model):
    """
    @brief Abstract base model for criminal offenses.

    @details
    Defines common fields and choices for different offense types.
    This class is abstract and is meant to be inherited by specific offense models.
    """
    FELONY = 'Felony'
    MISDEMEANOR = 'Misdemeanor'
    INFRACTION = 'Infraction'

    OFFENSE_TYPES = [
        (FELONY, 'Felony'),
        (MISDEMEANOR, 'Misdemeanor'),
        (INFRACTION, 'Infraction'),
    ]

    offense_type = models.CharField(max_length=20, choices=OFFENSE_TYPES)
    description = models.TextField()

    class Meta:
        abstract = True


class FederalOffense(CriminalOffense):
    """
    @brief Model for federal offenses.

    @details
    Extends CriminalOffense with federal-specific offense classes,
    representing different felony, misdemeanor, or infraction categories.
    """
    CLASS_CHOICES = [
        ('A', 'Class A'),  # Felony && Misdemeanor
        ('B', 'Class B'),
        ('C', 'Class C'),
        ('D', 'Class D'),  # Felony only
        ('E', 'Class E'),
        ('NA', 'Infraction'),  # Infraction only
    ]
    offense_class = models.CharField(max_length=2, choices=CLASS_CHOICES)

    @property
    def source(self):
        """
        @brief Indicates the source jurisdiction of the offense.

        @details
        This property returns the string "federal" to identify
        the offense as a federal offense.

        @return str Always returns 'federal'.
        """
        return "federal"

    def __str__(self):
        """
        @brief String representation of federal offense.

        @details
        Combines the offense class display label and description
        for easy identification.

        @return str Descriptive string of offense.
        """
        return f"{self.get_offense_class_display()} - {self.description}"


class VACodeOffense(CriminalOffense):
    """
    @brief Model for Virginia Code offenses.

    @details
    Extends CriminalOffense with Virginia Code-specific offense classes,
    representing felony, misdemeanor, or infraction categories.
    """
    CLASS_CHOICES = [
        ('1', 'Class 1'),  # Felony && Misdemeanor
        ('2', 'Class 2'),
        ('3', 'Class 3'),
        ('4', 'Class 4'),
        ('5', 'Class 5'),  # Felony only
        ('6', 'Class 6'),
        ('NA', 'Infraction'),  # Infraction only
    ]
    offense_class = models.CharField(max_length=2, choices=CLASS_CHOICES)

    @property
    def source(self):
        """
        @brief Indicates the source jurisdiction of the offense.

        @details
        This property returns the string "virginia" to identify
        the offense as a Virginia Code offense.

        @return str Always returns 'virginia'.
        """
        return "virginia"

    def __str__(self):
        """
        @brief String representation of VA Code offense.

        @details
        Combines the offense class display label and description
        for easy identification.

        @return str Descriptive string of offense.
        """
        return f"{self.get_offense_class_display()} - {self.description}"


class CriminalOffenseLink(models.Model):
    """
    @brief Links a criminal to one or more offenses.

    @details
    Allows association of a criminal with either a federal offense or
    a Virginia Code offense. Tracks the date charged and conviction status.
    """
    criminal = models.ForeignKey(Criminal, on_delete=models.CASCADE)
    federal_offense = models.ForeignKey(FederalOffense, null=True, blank=True, on_delete=models.CASCADE)
    vacode_offense = models.ForeignKey(VACodeOffense, null=True, blank=True, on_delete=models.CASCADE)

    date_charged = models.DateField(null=True, blank=True)
    convicted = models.BooleanField(default=False)

    def __str__(self):
        """
        @brief String representation linking criminal and offense description.

        @details
        Returns a string combining the criminal’s name with the linked offense's
        description or a placeholder if no offense is linked.

        @return str String combining criminal name and offense description.
        """
        offense_str = (
            str(self.federal_offense) if self.federal_offense else
            str(self.vacode_offense) if self.vacode_offense else
            "No offense"
        )
        return f"{self.criminal} - {offense_str}"
